import os, ast
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction


extension_icon = 'icon.png'
db_path = os.path.join(os.path.dirname(__file__), 'pastes.json')


class PasteExtension(Extension):

	def __init__(self):
		super(PasteExtension, self).__init__()
		self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

	def registerPaste(self,name,value):
		f = open(db_path, "w+")
		f.write(
			',{\n'
			+ '"name":"'
			+ name + ',\n'
			+ '"value":"'
			+ value + '"\n'
			+ '}'
		)
		f.close()

	def getPastes(self, searchvalue):
		temp = []
		try:
			with open(db_path, "rb") as f:
				db = eval(f.read().decode("utf-8"), dict(true=True, false=False, null=None), {})
				for row in db:
					if len(temp) >= 9:
						break
					if searchvalue in row.get("value"):
						temp.append(row)
				if len(temp) == 0:
					raise Exception("no gamers with that name HERE")
				return temp
		except FileNotFoundError:
			raise Exception("error 404 gamer not found")


class KeywordQueryEventListener(EventListener):

	def on_event(self, event, extension):

		search_term = ''.join(['%', event.get_argument().replace('%', ''), '%']) if event.get_argument() else None
		if not search_term:
			return RenderResultListAction([
				ExtensionResultItem(icon=extension_icon,
									name='Type in paste name...',
									on_enter=DoNothingAction())
			])
		search_terms = event.get_argument().replace('%', '').split(' ')
		search_term = ' '.join(search_terms)
		print(search_terms)
		print(' '.join(search_terms))
		if search_terms[0] == 'create':
			try:
				if not search_terms[1] and not search_terms[2]:
					return RenderResultListAction([
						ExtensionResultItem(icon=extension_icon,
											name='Type in new paste name and value',
											on_enter=DoNothingAction()),
						ExtensionResultItem(
											name='Format: [prefix] create <name of new paste> <value of new paste>',
											on_enter=DoNothingAction())
					])
			except: 
				return RenderResultListAction([
						ExtensionResultItem(icon=extension_icon,
											name='Type in new paste name and value',
											on_enter=DoNothingAction()),
						ExtensionResultItem(
											name='Format: [prefix] create <name of new paste> <value of new paste>',
											on_enter=DoNothingAction())
					])
			return RenderResultListAction([
				ExtensionResultItem(icon=extension_icon,
									name="Create paste \"" + search_terms[1] + "\" with value \"" + ' '.join(x for x in search_terms[2:])+"\"",
									on_enter=pe.registerPaste(search_terms[1]," ".join(x for x in search_terms[2:])))
			])

		items = []
		try:
			for row in pe.getPastes(' '.join(search_terms)):
				if len(items) < 8:
					items.append(ExtensionResultItem(icon=extension_icon,
													 name="Copy paste: "+row['name'].capitalize(),
													 on_enter=CopyToClipboardAction(row['value'])))
		except:
			return RenderResultListAction([
				ExtensionResultItem(icon=extension_icon,
									name='No pastes found with name "'+ ' '.join(search_terms)+ '"',
									on_enter=DoNothingAction()),
				ExtensionResultItem(icon=extension_icon,
									name='Add a paste with "cp create <name> <value>"',
									on_enter=DoNothingAction())
			])
		return RenderResultListAction(items)

pe = None
if __name__ == '__main__':
	pe = PasteExtension()
	pe.run()
