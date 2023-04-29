from dash import html, dcc
import dash_bootstrap_components as dbc


def generate_toast(_id, header='提示', icon='primary'):
    return dbc.Toast(
        id=_id,
        header=header,
        icon=icon,
        duration=3000,
        is_open=False,
        dismissable=True,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    )


def generate_modal(_id, text_id, close_id, title='提示', close='关闭', centered=True, backdrop=True):
    return dbc.Modal(
        id=_id,
        children=[
            dbc.ModalHeader(dbc.ModalTitle(title), close_button=True),
            dbc.ModalBody(id=text_id),
            dbc.ModalFooter(
                dbc.Button(
                    close,
                    id=close_id,
                    className="ms-auto",
                )
            ),
        ],
        centered=centered,
        backdrop=backdrop,
        is_open=False,
    )


def generate_tooltip(target, text):
    return dbc.Tooltip(
        children=text,
        target=target,
    ),
