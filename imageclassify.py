from aip import AipImageClassify
import asyncio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async

""" 你的 APPID AK SK """
APP_ID = '115520751'
API_KEY = '88ZD9NWCBWgp662Njy0X7CDr'
SECRET_KEY = 'StweIUyc0wToThpfQi2Mp1WxgPiTVRDE'

client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)

""" 读取图片 """


def get_file_content(filepath):
    #path = os.path.join('image', filepath)
    path = filepath
    with open(path, 'rb') as fp:
        return fp.read()


def classify(image_name):

    image = get_file_content(image_name)

    """ 调用通用物体和场景识别 """
    client.advancedGeneral(image)

    """ 如果有可选参数 """
    options = {}
    options["baike_num"] = 0

    """ 带参数调用通用物体和场景识别 """
    data = client.advancedGeneral(image, options)

    sentence_dict = {}
    i = 0
    for item in data['result']:
        sentence = '该图片里包含' + item['keyword'] + ',是' + item['root'] + '类型的。'
        sentence_dict[i] = sentence
        i += 1

    return sentence_dict


chat_msgs = []  # The chat message history. The item is (name, message content)
online_users = set()


def t(eng, chinese):
    """return English or Chinese text according to the user's browser language"""
    return chinese if 'zh' in session_info.user_language else eng


async def refresh_msg(my_name):
    """send new message to current session"""
    global chat_msgs
    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(0.5)
        for m in chat_msgs[last_idx:]:
            if m[0] != my_name:  # only refresh message that not sent by current user
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')


        last_idx = len(chat_msgs)


async def main():
    """PyWebIO chat room

    You can chat with everyone currently online.
    """
    global chat_msgs

    put_markdown(t("## PyWebIO chat room\nWelcome to the chat room, you can chat with all the people currently online. You can open this page in multiple tabs of your browser to simulate a multi-user environment. This application uses less than 90 lines of code, the source code is [here](https://github.com/wang0618/PyWebIO/blob/dev/demos/chat_room.py)", "## PyWebIO聊天室\n欢迎来到聊天室，你可以和当前所有在线的人聊天。你可以在浏览器的多个标签页中打开本页面来测试聊天效果。本应用使用不到90行代码实现，源代码[链接](https://github.com/wang0618/PyWebIO/blob/dev/demos/chat_room.py)"))

    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)
    nickname = await input(t("Your nickname", "请输入你的昵称"), required=True, validate=lambda n: t('This name is already been used', '昵称已被使用') if n in online_users or n == '📢' else None)

    online_users.add(nickname)
    chat_msgs.append(('📢', '`%s` joins the room. %s users currently online' % (nickname, len(online_users))))
    put_markdown('`📢`: `%s` join the room. %s users currently online' % (nickname, len(online_users)), sanitize=True, scope='msg-box')

    @defer_call
    def on_close():
        online_users.remove(nickname)
        chat_msgs.append(('📢', '`%s` leaves the room. %s users currently online' % (nickname, len(online_users))))

    refresh_task = run_async(refresh_msg(nickname))

    while True:

        image = await file_upload(t('upload an image', '上传一张图片'), placeholder=t('upload an image', '上传图片')),
        put_text("上传成功")
        open(image['filename'], 'wb').write(image['content'])

        language = actions(name='languages', buttons=['中文' , 'English', 'にほんご'])

        command = actions(name='cmd', buttons=[t('Send', '发送'), {'label': t('Exit', '退出'), 'type': 'cancel'}])

        classify_result = classify(image['filename'])

        if image is None:
            break

        for item in classify_result:
            put_markdown('`%s`: %s' % ('baidu', classify_result[item]), sanitize=True, scope='msg-box')
            chat_msgs.append((nickname, classify_result[item]))

    refresh_task.close()
    toast("You have left the chat room")



if __name__ == '__main__':
    start_server(main, 5704)
