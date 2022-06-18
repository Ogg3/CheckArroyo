
def writeHtmlReport():
    pass

def html_start():
    start = """
    <html>
<head>
<style>
* {
  font-family: 'Avenir';
}
.bubbleWrapper {
	padding: 10px 10px;
	display: flex;
	justify-content: flex-end;
	flex-direction: column;
	align-self: flex-end;
  color: #fff;
}
.inlineContainer {
  display: inline-flex;
}
.inlineContainer.own {
  flex-direction: row-reverse;
}
.inlineIcon {
  width:20px;
  object-fit: contain;
}
.ownBubble {
	min-width: 60px;
	max-width: 700px;
	padding: 14px 18px;
  margin: 6px 8px;
	background-color: #03C03C;
	border-radius: 16px 16px 0 16px;
	border: 1px solid #443f56;

}
.otherBubble {
	min-width: 60px;
	max-width: 700px;
	padding: 14px 18px;
  margin: 6px 8px;
	background-color: #0000FF;
	border-radius: 16px 16px 16px 0;
	border: 1px solid #54788e;

}
.own {
	align-self: flex-end;
}
.other {
	align-self: flex-start;
}
span.own,
span.other{
  font-size: 14px;
  color: grey;
}
</style>
</head>
<body>
    """
    return start


def html_participants(username, snapchatid):
    ret = """
    <div>
        Username: %s
        Snapchat ID: %s
    </div>
    """ % (username, snapchatid)
    return ret


def html_right_start(metadata):
    """

    """

    sender_snapchat_id = metadata[0]
    message_id = metadata[1]
    server_id = metadata[2]
    message_decoded = metadata[3]

    top = """
        <div class="bubbleWrapper">
            <div class="inlineContainer own">
                <div class="ownBubble own">
                <!--
    				Metadata
    				Sender snapchat id: %s
    				Message ID: %s
    				Server ID: %s
    				Message decoded: %s

    				-->
            """ % (sender_snapchat_id, message_id, server_id, message_decoded)

    return top


def html_right_end(username, message_type, timesent):
    bot = """
    			</div>
    		</div><span class="own">Username: %s Type: %s Sent: %s</span>
    	</div>
        """ % (username, message_type, timesent)

    return bot


def html_left_start(metadata):
    """

    """

    sender_snapchat_id = metadata[0]
    message_id = metadata[1]
    server_id = metadata[2]
    message_decoded = metadata[3]

    top = """
        <div class="bubbleWrapper">
            <div class="inlineContainer">
                <div class="otherBubble other">
                <!--
    				Metadata
    				Sender snapchat id: %s
    				Message ID: %s
    				Server ID: %s
    				Message decoded: %s

    				-->
            """ % (sender_snapchat_id, message_id, server_id, message_decoded)

    return top


def html_left_end(username, message_type, timesent, timerecived):
    """

    """
    bot = """
    			</div>
    		</div><span class="other">Username: %s Type: %s Sent: %s Recived: %s</span>
    	</div>
        """ % (username, message_type, timesent, timerecived)

    return bot


def html_video(path):
    """

    """
    ret = """
                <video src="../%s" style="max-height:400; max-width:600; align:left;" alt="" controls=""></video>
    """ % path

    return ret


def html_pic(path):
    """

    """
    ret = """
                <img src="../%s" style="max-height:400; max-width:600; align:left;" alt=""></img>
    """ % path

    return ret


def html_text(message):
    ret = """
                    %s
    """ % message
    return ret


def html_unknown():
    ret = """
                    <b><p style="color:red">UNKNOWN MESSAGE OR FILE TYPE</b>
    """
    return ret

def html_expert(message):
    ret = """
                    <b><p style="color:red">UNFILTERED DATA:</b><br>
                    %s
    """ % message
    return ret


def html_voicecall():
    """

    """


def html_end():
    end = """
</body>
    """
    return end

# So weird
if __name__ == '__main__':
    #main()
    pass