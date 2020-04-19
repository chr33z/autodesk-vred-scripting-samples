# Update scene geometry while a script is running

# This script will cycle through all variant sets that are not contained in a group
# and load the containing geometry. To test this example. you will have to create
# some variant sets that contain different geometries


import threading

variantsets = getGroupedVariantSets()['nogroup']
variantset_index = 0
total_cycle_count = 5

# Call this in a thread so that VRED actually shows the changes in the view
def changeVariantSet():
    global variantset_index
    global total_cycle_count
    
    if total_cycle_count > 0:
        selectVariantSet(variantsets[variantset_index], False)
        variantset_index = (variantset_index + 1) % len(variantsets)

        updateScenegraph(True)

        total_cycle_count = total_cycle_count - 1

# function that listens to messages from message receiver
def vrMessageService_receivedMessage(message_id, args): 
    # Use the VRED_MSG_CHANGED_SCENEGRAPH message to trigger the variantset change
    if message_id == vrController.VRED_MSG_CHANGED_SCENEGRAPH:
        print('VRED_MSG_CHANGED_SCENEGRAPH')
        threading.Timer(0.5, changeVariantSet).start()

# connect to message receiver
vrMessageService.message.connect(vrMessageService_receivedMessage)
updateScenegraph(True) #use this to 'trigger' the first message "VRED_MSG_CHANGED_SCENEGRAPH" 

# If you are done, disconnect from the message service
# vrMessageService.message.disconnect(vrMessageService_receivedMessage)