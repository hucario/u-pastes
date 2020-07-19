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
		self.allowed_skin_tones = ["", "dark", "light", "medium", "medium-dark", "medium-light"]

	def registerPaste(self,name,value):
		f = open(db_path, "w")
		f.write(
			'[{\n'
			+ '"name":"'
			+ name + ',\n'
			+ '"value":"'
			+ value + '"\n'
			+ '}]'
		)
		f.close()

	def getPastes(self, searchvalue):
		temp = []
		f = ast.literal_eval(db_path)
		for row in f:
			if len(temp) < 9 and (searchvalue in row.value):
				temp.append(f)


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
		search_terms.pop(0)
		if search_term.split(' ')[0] == 'create':
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
		for row in pe.getPastes(''.join(search_terms)):
			if len(items) < 8:
				items.append(ExtensionResultItem(icon=extension_icon,
												 name=row['name'].capitalize(),
												 on_enter=CopyToClipboardAction(row['value'])))

		return RenderResultListAction(items)

pe = None
if __name__ == '__main__':
	pe = PasteExtension()
	pe.run()
