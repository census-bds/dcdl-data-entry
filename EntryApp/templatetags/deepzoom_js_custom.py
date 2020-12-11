'''django-deepzoom template tag'''
from django import template

import logging
logger = logging.getLogger('EntryApp.tags')

register = template.Library()

def deepzoom_js(parser, token):
    try:
        tag_name, deepzoom_object, deepzoom_div_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("The %r tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'." % token.contents.split()[0])
    if (deepzoom_object[0] == deepzoom_object[-1] and deepzoom_object[0] in ('"', "'")):
        raise template.TemplateSyntaxError("The %r tag's 'Deep Zoom object' argument should not be in quotes." % tag_name)
    if not (deepzoom_div_id[0] == deepzoom_div_id[-1] and deepzoom_div_id[0] in ('"', "'")):
        raise template.TemplateSyntaxError("The %r tag's 'Deep Zoom div ID' argument should be in quotes." % tag_name)
    return DeepZoom_JSNode(deepzoom_object, deepzoom_div_id[1:-1])


class DeepZoom_JSNode(template.Node):
    def __init__(self, deepzoom_object, deepzoom_div_id):
        logger.debug(f'deepzoom_object from parser: \n\t {type(deepzoom_object)}')
        self.deepzoom_object = template.Variable(deepzoom_object)
        self.deepzoom_div_id = deepzoom_div_id
        logger.debug(f'self.deepzoom object: \n\t {self.deepzoom_object}')
    def render(self, context):
        try:
            dz_object = self.deepzoom_object.resolve(context)
            logger.debug(f'dz_object: \n \t {type(dz_object)}')
            logger.debug(f'self.deepzoom_div_id: \n \t {type(self.deepzoom_div_id)}')
            t = template.loader.get_template('deepzoom/deepzoom_js.html')
            return t.render({'deepzoom_object': dz_object, 
                             'deepzoom_div_id': self.deepzoom_div_id})
        except template.VariableDoesNotExist:
            return ''

register.tag('deepzoom_js', deepzoom_js)


#EOF - django-deepzoom template tag