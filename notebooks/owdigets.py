from io import BytesIO
from os import getenv
from pathlib import Path

from ipywidgets import (
    VBox,
    HBox,
    HTML,
    Layout,
    Tab,
    FileUpload,
    BoundedFloatText,
    Dropdown,
    Label,
    Checkbox,
    Text,
    Button,
    BoundedIntText,
    Image,
)

edo_color = {
    'blue': '#1f77b4',
    'orange': '#ec6f00',
    'green': '#2ca02c',
    'red': '#D20000',
    'purple': '#9467bd',
    'yellow': '#edb120',
    'pink': '#e377c2',
    'cyan': '#4dbeee',
    'gray': '#838383',
    # light
    'lightblue': '#aec7e8',
    'lightorange': '#ffbb7f',
    'lightgreen': '#98df8a',
    'lightred': '#ff9797',
    'lightpurple': '#c5b0d5',
    'lightyellow': '#FFD674',
    'lightpink': '#f7b6d2',
    'lightcyan': '#a4e4ff',
    'lightgray': '#bdbdbd',
    # dark
    'darkblue': '#004f85',
    'darkorange': '#884000',
    'darkgreen': '#266d26',
    'darkred': '#a70000',
    'darkpurple': '#640096',
    'darkyellow': '#b37f00',
    'darkpink': '#ca0065',
    'darkcyan': '#0098d9',
    'darkgray': '#3d3d3d',
}

margins = {
    'base_wdg': '1px 2px 1px 2px',
    'dropdown': '1px 2px 2px 2px',
    'tab': '3px 3px 3px 3px',
    'box': '0px 4px 6px 4px',
    'box_in_tab': '0px 0px 0px 0px',
    'box_content': '4px 4px 4px 4px',
    'title': '2px 0px 1px 7px',
    'loading': '4px 0px 0px 20px',
    'export': '4px 0 -4px 0px',
    'figure': '0px 0px 0px 0px',
}

pe_tab_height = '124px'

WIDGET_WIDTH = '235px'
HALF_WIDGET_WIDTH = '115px'
DESCRIPTION_WIDTH = '47%'

# TMP_DIR = Path(getenv('TEMP', '.'))
TMP_DIR = Path('.')

class OCheckbox(Checkbox):

    def __init__(self, name, **kwargs):
        width = kwargs.get('width', WIDGET_WIDTH)
        super().__init__(
            description=name,
            layout=kwargs.get(
                'layout', Layout(margin=margins['base_wdg'], width=width)
            ),
            **kwargs,
        )


class OText(Text):
    def __init__(self, name: str, **kwargs):
        width = kwargs.get('width', WIDGET_WIDTH)
        style = kwargs.get('style', {'description_width': DESCRIPTION_WIDTH})
        super().__init__(
            description=name,
            style=style,
            layout=kwargs.get(
                'layout', Layout(margin=margins['base_wdg'], width=width)
            ),
            **kwargs,
        )


class OBoundedText(BoundedFloatText):

    def __init__(self, name: str, value: float = 0.0, **kwargs):
        kwargs['min'] = kwargs.get('width', 0)
        kwargs['max'] = kwargs.get('width', 1e9)
        width = kwargs.get('width', WIDGET_WIDTH)
        style = kwargs.get('style', {'description_width': DESCRIPTION_WIDTH})
        super().__init__(
            value=value,
            description=name,
            style=style,
            layout=kwargs.get(
                'layout', Layout(margin=margins['base_wdg'], width=width)
            ),
            **kwargs,
        )


class OBoundedIntText(BoundedIntText):

    def __init__(self, name: str, value: int = 0, **kwargs):
        kwargs['min'] = kwargs.get('width', 0)
        kwargs['max'] = kwargs.get('width', 100)
        width = kwargs.get('width', WIDGET_WIDTH)
        style = kwargs.get('style', {'description_width': DESCRIPTION_WIDTH})
        super().__init__(
            value=value,
            description=name,
            style=style,
            layout=kwargs.get(
                'layout', Layout(margin=margins['base_wdg'], width=width)
            ),
            **kwargs,
        )


class ODropdown(Dropdown):

    def __init__(self, name, value, options, **kwargs):
        width = kwargs.get('width', WIDGET_WIDTH)
        style = kwargs.get('style', {'description_width': DESCRIPTION_WIDTH})
        super().__init__(
            options=options,
            value=value,
            description=name,
            style=style,
            layout=Layout(margin=margins['dropdown'], width=width),
            **kwargs,
        )


class OFrameBox(Label):

    def __init__(self, name: str = '', value: str = '', **kwargs):
        kwargs['layout'] = kwargs.get(
            'layout',
            Layout(margin='0 0 0 0', width='3px', height='auto', grid_area='sidebar'),
        )
        kwargs['style'] = kwargs.get(
            'style', {'description_width': '0%', 'button_color': '#6b6b6b'}
        )
        super().__init__(description=name, value=value, **kwargs)


class OButton(Button):
    def __init__(self, name, call_back, **kwargs):
        super().__init__(description=name, layout=Layout( width=kwargs.get('width', '80px'), margin='10px 10px 10px 10px'))
        self.on_click(self.on_button_clicked)
        self._cb = call_back

    def on_button_clicked(self, event):
        self._cb()


class OFileUpload(HBox):

    def __init__(self, name, tooltip, **kwargs):
        self._working_dir = kwargs.get('working_dir', TMP_DIR)
        width = kwargs.get('width', HALF_WIDGET_WIDTH)
        layout = Layout(margin=margins['box'], width=width, justify_content='flex-end')
        self.upload_widget = FileUpload(description='Upload file...', tooltip=tooltip, layout={'width': width})
        widgets = [
            Label(name, layout=layout),
            self.upload_widget,
        ]
        super().__init__(widgets)
        self.upload_widget.observe(self.on_file_upload, names='value')
        self._file_path = None

    def on_file_upload(self, change):
        for data in change['new']:
            name = data['name']
            self._file_path = f'{TMP_DIR}/{name}'
            with open(self._file_path, 'wb') as fp:
                fp.write(data['content'])
            self.upload_widget.description = name


class OColoredBbox(HBox):

    def __init__(self, color='darkpurple', **kwargs):
        if color[0] != '#':
            color = edo_color[color]
        frames = [
            OFrameBox(),
            OFrameBox(style={'description_width': '0%', 'button_color': color}),
            OFrameBox(),
        ]
        super().__init__(frames, **kwargs)


class OPanel(HBox):

    def __init__(self, name, data: dict, buttons: list = None, **kwargs):
        self.tab = None
        self._height = kwargs.get('height', pe_tab_height)
        self._data = {}
        color = kwargs.get('color', 'darkpurple')
        colored_box = OColoredBbox(color)
        tabs = self._build_tabs(data)
        html = f''' 
            <p style='font-family:calibri;font-size:147%;'>
                <font color='{color}'>⬙</font>
                <b>{name}</b>
            </p>
        '''
        widgets = [ 
            HTML( value=html, layout=Layout(margin=margins['title'], align_items='flex-start'), ),
            tabs,
        ]
        if buttons:
            button_bar = HBox(buttons)            
            widgets.append(button_bar)
        bar = VBox(widgets, layout=Layout(width='auto', flex='1 1 auto', margin=margins['box_content']), )
        super().__init__(
            [colored_box, bar],
            layout=Layout(
                margin=margins['box'], 
                border='solid 1px' + '#6b6b6b',
                ),
        )

    def _build_tabs(self, data):
        layout = Layout(
            margin=margins['box_in_tab'],
            height=self._height,
            align_content='flex-start',
        )
        panels = []
        for fields_desc in data.values():
            children = []
            for field_desc in fields_desc:
                name = field_desc.get('name')
                if 'customWidget' in field_desc:
                    obj = field_desc['customWidget']
                else:
                    class_name = field_desc.get('type')
                    dyn_class = globals()[class_name]
                    obj = dyn_class(**field_desc)
                children.append(obj)
                if name:
                    self._data[name] = obj
                    obj.name = name
            panel = VBox(children, layout=layout)
            for obj in children:
                obj.parent = panel
            panels.append(panel)
        self._tab = Tab(panels, layout=Layout(margin=margins['tab']))
        for i, panel_name in enumerate(data):
            self._tab.set_title(i, panel_name)
        return self._tab
    
    def __getitem__(self, name: str):
        return self._data[name]
