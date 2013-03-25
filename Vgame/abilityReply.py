import cjson

class AbilityReply():
	def __init__(self):
		self.reset()

	def reset(self):
		self.reply = dict.fromkeys(('map', 'info', 'actions', 'messages', 'character', 'equipment'), False)
		self.reply['ability_text'] = ""
		
	def setAll(self):
		self.reply.update(dict.fromkeys(('map', 'info', 'actions', 'messages', 'character', 'equipment'), True))
	
	def setReply(self, replyName):
		self.reply[replyName] = True
		
	def mergeReply(self, mergingR):
		for k in mergingR.reply.keys():
			if mergingR.reply[k]:
				self.reply[k] = mergingR.reply[k]
	
	def setAbilityText(self, text):
		self.reply['ability_text'] = text

	def outputJSON(self):
		return cjson.encode(self.reply)