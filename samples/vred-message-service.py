# Using the vrMessageService
# --------------------------------

# The vrMessageService provides callbacks for internal states of VRED. The message
# service can be used to listen for these states on manage your plugins resources,
# save data, clean he scene, etc. etc. pp.
# The vrMessageService is not documented (as of now) but offers many messages that
# are listed in the function 'check_vrControllerMessage.

# This examples hooks to the message service and triggers some events that are
# then received via the message service hook.


import vrController
import vrScenegraph

def check_vrControllerMessage(message_id):
    messages = ('VRED_MSG_ARGV',
        'VRED_MSG_CHANGED_CAMERA_UP',
        'VRED_MSG_CHANGED_MATERIAL',
        'VRED_MSG_CHANGED_PB_PARAMETERS',
        'VRED_MSG_CHANGED_SCENEGRAPH',
        'VRED_MSG_CONVERT_OSF_FILE',
        'VRED_MSG_DESELECTED_NODE',
        'VRED_MSG_EXPORTED_FILE',
        'VRED_MSG_IDLE',
        'VRED_MSG_IMPORTED_FILE',
        'VRED_MSG_INIT',
        'VRED_MSG_KEY_PRESSED',
        'VRED_MSG_KEY_RELEASED',
        'VRED_MSG_LOADED_GEOMETRY',
        'VRED_MSG_LOOP',
        'VRED_MSG_NEW_SCENE',
        'VRED_MSG_NONE',
        'VRED_MSG_PRENEW_SCENE',
        'VRED_MSG_PRE_QUIT',
        'VRED_MSG_PROJECT',
        'VRED_MSG_PROJECT_LOADED',
        'VRED_MSG_PROJECT_MERGED',
        'VRED_MSG_SAVED_GEOMETRY',
        'VRED_MSG_SELECTED_CAMERA',
        'VRED_MSG_SELECTED_LIGHT',
        'VRED_MSG_SELECTED_MATERIAL',
        'VRED_MSG_SELECTED_NODE',
        'VRED_MSG_SWITCH_MATERIAL_CHANGED',
        'VRED_MSG_UPDATE_UI',
        'VRED_MSG_USER',)

    for message in messages:
        if int(message_id) == int(getattr(vrController, message)):
            return message



def vrMessageService_receivedMessage(self, message_id, args):
    print(check_vrControllerMessage(message_id))

    if message_id == vrController.VRED_MSG_PRENEW_SCENE:
        print("VRED_MSG_PRENEW_SCENE: New scene will be loaded.")

    if message_id == vrController.VRED_MSG_NEW_SCENE:
        print("VRED_MSG_NEW_SCENE: New scene will be loaded.")

    if message_id == vrController.VRED_MSG_CHANGED_SCENEGRAPH:
        print("VRED_MSG_CHANGED_SCENEGRAPH: Scenegraph has changed.")

    if message_id == vrController.VRED_MSG_IDLE:
        print("VRED_MSG_IDLE: VRED is idle.")

    if message_id == vrController.VRED_MSG_PROJECT_LOADED:
        print("VRED_MSG_PROJECT_LOADED: Project has loaded.")


vrMessageService.message.connect(self.vrMessageService_receivedMessage)

# Update the scenegraph to receive a callback from the message service
updateScenegraph(True)

# Send an explicit message to the messageService callback to trigger something
self.vrMessageService_receivedMessage(vrController.VRED_MSG_NEW_SCENE, None)

# ...