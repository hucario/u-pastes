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
		search_terms = search_term.split(' ')
		if search_term.split(' ')[0] == 'create':
			search_terms.pop(0)
			if not search_terms[0] or not search_terms[1]:
				return RenderResultListAction([
					ExtensionResultItem(icon=extension_icon,
										name='Type in new paste name and value',
										on_enter=DoNothingAction()),
					ExtensionResultItem(
										name='Format: [prefix] create <name of new paste> <value of new paste>',
										on_enter=DoNothingAction())
				])
			b = search_terms.pop(0)
			return RenderResultListAction([
				ExtensionResultItem(icon=extension_icon,
									name="Create paste \"" + b + "\" with value \"".join(x for x in search_terms)+"\"",
									on_enter=pe.registerPaste(b,"".join(x for x in search_terms)))
			])

		items = []
		search_terms.pop(0)
		try:
			for row in pe.getPastes(''.join(search_terms)):
				if len(items) < 8:
					items.append(ExtensionResultItem(icon=extension_icon,
													 name=row['name'].capitalize(),
													 on_enter=CopyToClipboardAction(row['value'])))
		except:
			return RenderResultListAction([
				ExtensionResultItem(icon=extension_icon,
									name='No pastes found. Add a paste with "cp create <name of paste> <value of paste>"',
									on_enter=DoNothingAction())
			])
		return RenderResultListAction(items)

pe = None
if __name__ == '__main__':
	pe = PasteExtension()
	pe.run()
