import os
from typing import Any
import asyncio
from supabase import create_client, AuthApiError, AuthError
from postgrest import APIError
from dotenv import load_dotenv
import datetime
import flet as ft
from flet import Container, Row
import inspect
from flet_datatable2 import DataTable2, DataRow2, DataColumnSize, DataColumn2
import stdiomask

@ft.control
class UniversalDateInput(ft.Container):
    def __init__(self, page: ft.Page) -> None:
        self.app_page = page  
        
        self.today = datetime.datetime.today()
        self.selected_date = datetime.datetime.today().strftime('%m/%d/%Y')
        self.date_selected_text = ft.Text(
            value="",
            size=14,
            color=ft.Colors.GREY_300,
            weight=ft.FontWeight.W_500
        )
        
        self.date_picker = ft.DatePicker(
            last_date=self.today,
            on_change=self.date_picked,
        )

        
        super().__init__(
            width=300,
            height=52,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            border_radius=ft.BorderRadius.all(10),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border.all(1, ft.Colors.GREY_800),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.CALENDAR_TODAY,
                                size=17,
                                color=ft.Colors.PURPLE_300
                            ),
                            self.date_selected_text,
                        ]
                    ),
                    ft.Button(
                        width=140,
                        height=36,
                        icon=ft.Icons.CALENDAR_MONTH,
                        content="Pick Date",
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.PURPLE_700,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda _: self.app_page.show_dialog(self.date_picker)
                    )
                ]
            )
        )
    
    def date_picked(self, e):
        self.selected_date = e.control.value.strftime('%m/%d/%Y')
        self.date_selected_text.value = f'{self.selected_date}'
        self.date_selected_text.color = ft.Colors.GREY_200


@ft.control
class Workouts_Table(Container):
    def __init__(self, page: ft.Page, data, on_tap_function) -> None:
        self.app_page = page
        self.on_tap_function = on_tap_function
        self.data = data
       
        
        self.row_list = []
        
        def handle_tap():
            if inspect.iscoroutinefunction(self.on_tap_function):
                return lambda e, num = workout['id']: self.app_page.run_task(self.on_tap_function ,e,num)
            else:
                return lambda e, num = workout['id']: self.on_tap_function(e,num)
        
                
        for id, workout in enumerate(self.data, 1):
                self.row_list.append(
                    DataRow2(
                        cells=[
                            ft.DataCell(
                                content=ft.Text(
                                    str(id),
                                    size=13,
                                    color=ft.Colors.GREY_400,
                                    weight=ft.FontWeight.W_500
                                )
                            ),
                            ft.DataCell(
                                content=ft.Text(
                                    f'{workout['name']}',
                                    size=14,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_500
                                )
                            ),
                            ft.DataCell(
                                content=ft.Text(
                                    f'{workout['date']}',
                                    size=13,
                                    color=ft.Colors.GREY_400
                                )
                            ),
                            ft.DataCell(
                                content=ft.Text(
                                    f'{workout['notes']}',
                                    size=13,
                                    color=ft.Colors.GREY_400
                                )
                            ),
                        ],
                        on_tap=handle_tap()
                    )
                )
        
        super().__init__(
            border=ft.Border.all(1, ft.Colors.GREY_800),
            border_radius=ft.BorderRadius.all(14),
            bgcolor=ft.Colors.GREY_900,
            padding=ft.Padding.all(8),
            content=Row(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    DataTable2(
                        width=1000,
                        heading_row_height=48,
                        column_spacing=22,
                        heading_row_color=ft.Colors.GREY_900,
                        columns=[
                            DataColumn2(
                                size=DataColumnSize.S,
                                label=ft.Text(
                                    "#",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PURPLE_300
                                ),
                                tooltip="Number",
                                numeric=True
                            ),
                            DataColumn2(
                                size=DataColumnSize.L,
                                label=ft.Text(
                                    "WORKOUT",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PURPLE_300
                                ),
                                tooltip="Workout"
                            ),
                            DataColumn2(
                                size=DataColumnSize.L,
                                label=ft.Text(
                                    "DATE",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PURPLE_300
                                ),
                                tooltip="Date"
                            ),
                            DataColumn2(
                                size=DataColumnSize.L,
                                label=ft.Text(
                                    "NOTES",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PURPLE_300
                                ),
                                tooltip="Notes"
                            ),
                        ],
                        rows=self.row_list
                    )
                ]
            )
        )
        


def init_database():
    load_dotenv()

    url = os.environ.get("URL")
    key = os.environ.get("KEY")

    if not url or not key:
        raise ValueError("Missing required environment variables: URL and KEY")

    return create_client(
        url, 
        key,
    )


            
                    
@ft.control
class Page_Switch_Button(ft.Button):
    def __init__(self, page, route) -> None:
        self.app_page = page
        self.route = route
        
        self.display_string = str(route[1:])
        
        super().__init__(
            content=f'Go to {self.display_string.title()}',
            height=44,
            width=190,
            color=ft.Colors.GREY_200,
            bgcolor=ft.Colors.GREY_900,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_800),
            ),
            on_click= self.push
        )
    
    async def push(self):
        await self.app_page.push_route(self.route)


class Auth():
    def __init__(self, page, app_connector) -> None:
        self.app_page = page
        self.app_connector :App_to_Backend_Connector = app_connector
        self.type_of_user = ''
        
        self.sign_up_controls = {
            'email' : ft.TextField(
                label='Email',
                width=300,
                height=52,
                border_radius=10,
                bgcolor=ft.Colors.GREY_900,
                border_color=ft.Colors.GREY_800,
                focused_border_color=ft.Colors.PURPLE_500,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                cursor_color=ft.Colors.PURPLE_300
            ),
            'password' : ft.TextField(
                label='Password',
                password=True,
                can_reveal_password=True,
                width=300,
                height=52,
                border_radius=10,
                bgcolor=ft.Colors.GREY_900,
                border_color=ft.Colors.GREY_800,
                focused_border_color=ft.Colors.PURPLE_500,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                cursor_color=ft.Colors.PURPLE_300
            ),
            'checkbox' : ft.Checkbox(
                label="Check for sign-up (NOT sign-in)",
                label_style=ft.TextStyle(
                    color=ft.Colors.GREY_400,
                    size=13
                ),
                check_color=ft.Colors.WHITE,
                active_color=ft.Colors.PURPLE_600
            ),
            
        }
        
        self.error_bar = ft.Container(
            visible=False,
            width=300,
            height=95,
            bgcolor=ft.Colors.RED_900,
            border=ft.Border.all(1, ft.Colors.RED_700),
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(10)
        )
        
        self.view = ft.View(
            padding= ft.Padding.all(16),
            bgcolor=ft.Colors.BLACK,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=360,
                        padding=ft.Padding.all(28),
                        bgcolor=ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=ft.BorderRadius.all(20),
                        shadow=ft.BoxShadow(
                            blur_radius=30,
                            spread_radius=2,
                            color=ft.Colors.BLACK
                        ),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                            controls=[
                                ft.Container(
                                    width=54,
                                    height=54,
                                    border_radius=ft.BorderRadius.all(16),
                                    bgcolor=ft.Colors.PURPLE_900,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(
                                        ft.Icons.FITNESS_CENTER,
                                        size=27,
                                        color=ft.Colors.PURPLE_200
                                    )
                                ),
                                ft.Text(
                                    "Workout Logger",
                                    size=29,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    "Track your training. Keep your progress.",
                                    size=13,
                                    color=ft.Colors.GREY_500,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Divider(
                                    color=ft.Colors.GREY_800,
                                    height=10
                                ),
                                *self.sign_up_controls.values(),
                                ft.Button(
                                    content="Continue",
                                    width=300,
                                    height=48,
                                    bgcolor=ft.Colors.PURPLE_700,
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    on_click= lambda e: asyncio.create_task(self.check(e))
                                ),
                                self.error_bar
                            ]
                        )
                    )
                ),
            ]
        )
        
        
    async def check(self, e):
        checkbox = self.sign_up_controls.get('checkbox')
        email = self.sign_up_controls.get('email')
        password = self.sign_up_controls.get('password')
        
        if checkbox is not None and email is not None and password is not None:
            if checkbox.value:
                try:
                    placeholder = self.app_connector.sign_up(email=email.value,password=password.value)
                    
                    print('signing up...')
                    
                    await self.app_page.push_route("/home")
                    
                except (AuthError,AuthApiError) as error:
                    self.error_bar.visible = True
                    self.error_bar.content = ft.Column(controls=[ft.Text("Error:"), ft.Text(str(error))], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    self.app_page.update()
                    
                    await asyncio.sleep(2)
                    
                    self.error_bar.visible = False
                    self.app_page.update()
                    
            
            elif not checkbox.value:
                try:
                    placeholder = self.app_connector.sign_in(email=email.value,password=password.value)
                    
                    print('logging in...')
                    
                    await self.app_page.push_route("/home")
                    
                except (AuthError,AuthApiError) as error:
                    self.error_bar.visible = True
                    self.error_bar.content = ft.Column(controls=[ft.Text("Error:"), ft.Text(str(error))], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    self.app_page.update()
                    
                    await asyncio.sleep(2)
                                        
                    self.error_bar.visible = False
                    self.app_page.update()
                
            else:
                print("ERROR")
                
class Home():
    def __init__(self, page, app_connector) -> None:
        self.app_page = page
        self.app_connector :App_to_Backend_Connector = app_connector
        
        
        self.buttons = [
            
        ]
        self.view = ft.View(
            padding=ft.Padding.all(16),
            bgcolor=ft.Colors.BLACK,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=360,
                        padding=ft.Padding.all(28),
                        bgcolor=ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=ft.BorderRadius.all(20),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                            controls=[
                                ft.Container(
                                    width=58,
                                    height=58,
                                    border_radius=ft.BorderRadius.all(17),
                                    bgcolor=ft.Colors.PURPLE_900,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(
                                        ft.Icons.DASHBOARD_ROUNDED,
                                        size=28,
                                        color=ft.Colors.PURPLE_200
                                    )
                                ),
                                ft.Text(
                                    "Home",
                                    size=31,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    "Your training workspace",
                                    size=14,
                                    color=ft.Colors.GREY_500
                                ),
                                ft.Divider(
                                    color=ft.Colors.GREY_800,
                                    height=8
                                ),
                                ft.Container(
                                    width=300,
                                    padding=ft.Padding.all(16),
                                    bgcolor=ft.Colors.GREY_900,
                                    border_radius=ft.BorderRadius.all(12),
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.ADD_CHART,
                                                color=ft.Colors.PURPLE_300,
                                                size=22
                                            ),
                                            ft.Column(
                                                spacing=2,
                                                controls=[
                                                    ft.Text(
                                                        "Manage workouts",
                                                        size=14,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.WHITE
                                                    ),
                                                    ft.Text(
                                                        "Create or review your sessions",
                                                        size=12,
                                                        color=ft.Colors.GREY_500
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        Page_Switch_Button(
                                            page=self.app_page,
                                            route='/add'
                                        ),
                                        Page_Switch_Button(
                                            page=self.app_page,
                                            route='/all'
                                        ),
                                        ft.Button(
                                            content="Signout",
                                            height=44,
                                            width=190,
                                            color=ft.Colors.GREY_200,
                                            bgcolor=ft.Colors.GREY_900,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=10),
                                                side=ft.BorderSide(1, ft.Colors.GREY_800),
                                            ),
                                            on_click= lambda: asyncio.create_task(self.signout_button())
                                        )
                                    ]
                                )
                            
                            ]
                        )
                    )
                ),
            ]
        )
    
    async def signout_button(self):
        self.app_connector.sign_out()
        await self.app_page.push_route("/auth")
                   
class Add_Workout():
    def __init__(self, page, app_connector) -> None:
        self.app_page = page
        self.app_connector :App_to_Backend_Connector = app_connector
        
        self.data = {}
        
        self.add_workout_inputs = {
            'name' : ft.TextField(
                label="Workout Name",
                width=300,
                height=52,
                border_radius=10,
                bgcolor=ft.Colors.GREY_900,
                border_color=ft.Colors.GREY_800,
                focused_border_color=ft.Colors.PURPLE_500,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                cursor_color=ft.Colors.PURPLE_300
            ),
            'date' : UniversalDateInput(page=self.app_page),
            'notes' : ft.TextField(
                label="Notes",
                width=300,
                min_lines=4,
                max_lines=6,
                border_radius=10,
                bgcolor=ft.Colors.GREY_900,
                border_color=ft.Colors.GREY_800,
                focused_border_color=ft.Colors.PURPLE_500,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                cursor_color=ft.Colors.PURPLE_300
            ),
        }
        
        self.error_bar = ft.Container(
            visible=False,
            width=300,
            height=95,
            bgcolor=ft.Colors.RED_900,
            border=ft.Border.all(1, ft.Colors.RED_700),
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(10)
        )
        
        self.view = ft.View(
            padding=ft.Padding.all(16),
            bgcolor=ft.Colors.BLACK,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=360,
                        padding=ft.Padding.all(25),
                        bgcolor=ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=ft.BorderRadius.all(20),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Row(
                                    spacing=12,
                                    controls=[
                                        ft.Container(
                                            width=42,
                                            height=42,
                                            border_radius=ft.BorderRadius.all(12),
                                            bgcolor=ft.Colors.PURPLE_900,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(
                                                ft.Icons.ADD,
                                                size=22,
                                                color=ft.Colors.PURPLE_200
                                            )
                                        ),
                                        ft.Column(
                                            spacing=1,
                                            controls=[
                                                ft.Text(
                                                    "Add Workout",
                                                    size=25,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.WHITE
                                                ),
                                                ft.Text(
                                                    "Log a new training session",
                                                    size=12,
                                                    color=ft.Colors.GREY_500
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                ft.Divider(
                                    color=ft.Colors.GREY_800,
                                    height=8
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=13,
                                    controls=[
                                        *self.add_workout_inputs.values(),
                                        ft.Button(
                                            content="Add Workout",
                                            width=300,
                                            height=48,
                                            bgcolor=ft.Colors.PURPLE_700,
                                            color=ft.Colors.WHITE,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=10)
                                            ),
                                            on_click=lambda e: asyncio.create_task(self.add_workout(e))
                                        ),
                                        self.error_bar,
                                        Page_Switch_Button(
                                            page=self.app_page,
                                            route='/home'
                                        )
                                    ]
                                )
                            
                            ]
                        )
                    )
                ),
            ]
        )
    
    async def add_workout(self, e):
        for name, control in self.add_workout_inputs.items():
            if isinstance(control, UniversalDateInput):
                date_format = "%m/%d/%Y"
                dt_object = datetime.datetime.strptime(control.selected_date, date_format)
                
                self.data[name] = dt_object.date().isoformat()
            
            else:
                self.data[name] = control.value
        try:
            response = self.app_connector.add_workout(name=self.data['name'],date=self.data['date'],notes=self.data['notes'])
            
            self.error_bar.visible = True
            self.error_bar.bgcolor = ft.Colors.LIGHT_GREEN_900
            self.error_bar.border=ft.Border.all(1, ft.Colors.LIGHT_GREEN_600)
            self.error_bar.content = ft.Column(controls=[ft.Text("Success!")], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.app_page.update()
            
            await asyncio.sleep(2)
            
            self.error_bar.visible = False
            self.app_page.update()
            
        except (APIError, TypeError) as error:
            self.error_bar.visible = True
            self.error_bar.content = ft.Column(controls=[ft.Text("Error:"), ft.Text(str(error))], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.app_page.update()
            
            await asyncio.sleep(2)
            
            self.error_bar.visible = False
            self.app_page.update()
        
class All_Workouts():
    def __init__(self, page, app_connector) -> None:
        self.app_page = page
        self.app_connector :App_to_Backend_Connector = app_connector

       

        self.workouts = ft.Container(
            content=Workouts_Table(
                page=self.app_page,
                data=self.app_connector.all_workouts,
                on_tap_function=self.go_to_workout_info
            )
        )
        
        self.view = ft.View(
            padding=ft.Padding.all(16),
            bgcolor=ft.Colors.BLACK,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=360,
                        padding=ft.Padding.all(20),
                        bgcolor=ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=ft.BorderRadius.all(20),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(
                                                    "Workouts",
                                                    size=27,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.WHITE
                                                ),
                                                ft.Text(
                                                    "Your training history",
                                                    size=12,
                                                    color=ft.Colors.GREY_500
                                                )
                                            ]
                                        ),
                                        ft.Container(
                                            width=42,
                                            height=42,
                                            border_radius=ft.BorderRadius.all(12),
                                            bgcolor=ft.Colors.PURPLE_900,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(
                                                ft.Icons.FITNESS_CENTER,
                                                size=21,
                                                color=ft.Colors.PURPLE_200
                                            )
                                        )
                                    ]
                                ),
                                ft.Divider(
                                    color=ft.Colors.GREY_800,
                                    height=8
                                ),
                                ft.Container(
                                    width=320,
                                    height=420,
                                    content=self.workouts
                                ),
                                Page_Switch_Button(
                                    page=self.app_page,
                                    route='/home'
                                )
                            ]
                        )
                    )
                ),
            ]
        )
                
    async def go_to_workout_info(self,e, num):
        self.app_connector.workout = num
        await self.app_page.push_route('/card')
        
class Workout_Card_Page():
    def __init__(self, page, app_connector) -> None:
        self.app_page :ft.Page = page
        self.app_connector :App_to_Backend_Connector = app_connector


        for workout in self.app_connector.all_workouts:
            if workout['id'] == self.app_connector.workout:
                self.text = ft.Column(
                    controls=[
                        ft.Text(
                            workout['name'].title(),
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        ft.Row(
                            spacing=7,
                            controls=[
                                ft.Icon(
                                    ft.Icons.CALENDAR_TODAY,
                                    size=15,
                                    color=ft.Colors.PURPLE_300
                                ),
                                ft.Text(
                                    workout['date'],
                                    size=13,
                                    color=ft.Colors.GREY_500
                                )
                            ]
                        ),
                        ft.Divider(
                            color=ft.Colors.GREY_800,
                            height=12
                        ),
                        ft.Text(
                            workout['notes'],
                            size=15,
                            color=ft.Colors.GREY_300
                        ),
                    ],
                    spacing=12
                )
            

        
        
        self.delete_button = ft.Button(
            content='Delete (long press)',
            width=190,
            height=44,
            color=ft.Colors.RED_300,
            bgcolor=ft.Colors.RED_900,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.RED_900)
            ),
            on_long_press= lambda: self.delete_function()
        )
        
        self.edit_button = ft.Button(
            content='Edit',
            width=190,
            height=44,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PURPLE_700,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click= lambda: self.edit_function()
        )
        

       
        
        self.view = ft.View(
            padding=ft.Padding.all(16),
            bgcolor=ft.Colors.BLACK,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=360,
                        padding=ft.Padding.all(25),
                        bgcolor=ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=ft.BorderRadius.all(20),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "Workout",
                                            size=13,
                                            color=ft.Colors.PURPLE_300,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Container(
                                            width=38,
                                            height=38,
                                            border_radius=ft.BorderRadius.all(11),
                                            bgcolor=ft.Colors.GREY_900,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(
                                                ft.Icons.FITNESS_CENTER,
                                                size=18,
                                                color=ft.Colors.PURPLE_300
                                            )
                                        )
                                    ]
                                ),
                                ft.Container(
                                    padding=ft.Padding.only(top=5, bottom=8),
                                    content=self.text
                                ),
                                ft.Divider(
                                    color=ft.Colors.GREY_800,
                                    height=5
                                ),
                                self.edit_button,
                                self.delete_button,
                                Page_Switch_Button(
                                    page=self.app_page,
                                    route='/all'
                                )
                            ]
                        )
                    )
                ),
            ]
        )

          
    def delete_function(self):
        self.app_connector.delete_workout(self.app_connector.workout)
        self.app_connector.workout = ''
        
        self.text.controls = [
            ft.Container(
                padding=ft.Padding.all(20),
                border_radius=ft.BorderRadius.all(14),
                bgcolor=ft.Colors.GREY_900,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            size=42,
                            color=ft.Colors.PURPLE_300
                        ),
                        ft.Text(
                            "Deleted",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            "Workout removed successfully.",
                            size=13,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER
                        )
                    ]
                )
            )
        ]
        
        self.delete_button.visible = False
        self.edit_button.visible = False
        
        
        
    
    def edit_function(self):
        for workout in self.app_connector.all_workouts:
            if workout['id'] == self.app_connector.workout:
                self.name_field = ft.TextField(
                    label="Name",
                    value=workout['name'],
                    width=300,
                    height=52,
                    border_radius=10,
                    bgcolor=ft.Colors.GREY_900,
                    border_color=ft.Colors.GREY_800,
                    focused_border_color=ft.Colors.PURPLE_500,
                    color=ft.Colors.WHITE,
                    label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                    cursor_color=ft.Colors.PURPLE_300
                )

                self.date_field = UniversalDateInput(page=self.app_page)
                date_format = "%Y-%m-%d"
                datetime_obj = datetime.datetime.strptime(workout['date'], date_format)
                self.date_field.selected_date = datetime_obj
                self.date_field.date_selected_text.value = workout['date']

                self.notes_field = ft.TextField(
                    label="Notes",
                    value=workout['notes'],
                    multiline=True,
                    min_lines=3,
                    max_lines=6,
                    width=300,
                    border_radius=10,
                    bgcolor=ft.Colors.GREY_900,
                    border_color=ft.Colors.GREY_800,
                    focused_border_color=ft.Colors.PURPLE_500,
                    color=ft.Colors.WHITE,
                    label_style=ft.TextStyle(color=ft.Colors.GREY_500),
                    cursor_color=ft.Colors.PURPLE_300
                )

                self.text.controls = [
                    ft.Text(
                        "Edit Workout",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    self.name_field,
                    self.date_field,
                    self.notes_field,
                ]
                
                self.submit_edits = ft.Button(
                    content='Save Changes',
                    width=190,
                    height=44,
                    bgcolor=ft.Colors.PURPLE_700,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=lambda: asyncio.create_task(self.submit_button_on_click())
                )

        self.view.controls = [
            self.text,
            self.submit_edits,
            Page_Switch_Button(
                page=self.app_page,
                route='/all'
            )
        ]
        
        self.app_page.update()
    
    async def submit_button_on_click(self):
        edited_name =self.name_field.value
        edited_date =self.date_field.selected_date
        edited_notes =self.notes_field.value
        
        date_format = "%m/%d/%Y"
        dt_object = datetime.datetime.strptime(edited_date, date_format)
        
        edited_date = dt_object.date().isoformat()

        self.app_connector.edit_workout(self.app_connector.workout, edited_name, edited_date, edited_notes)
        
        await self.app_page.push_route('/home')
        await self.app_page.push_route('/card')
        
            
class Router():
    @staticmethod
    def get_page(route, page, app_connector):
        match route:
            case "/auth":
                return Auth(page, app_connector).view
            case "/home":
                return Home(page, app_connector).view
            case "/add":
                return Add_Workout(page, app_connector).view
            case "/all":
                return All_Workouts(page, app_connector).view
            case "/card":
                return Workout_Card_Page(page, app_connector).view
            
class App_to_Backend_Connector():
    def __init__(self, supabase) -> None:
        self.supabase = supabase
        self.all_workouts = []
        self.workout = ''
        
    def sign_up(self, email, password):
        response = self.supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password
                    }
                )

        return response
    
    def sign_in(self, email, password):
            response = self.supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )
    
            return response
    
    def add_workout(self, name, date, notes):
        data = self.supabase.auth.get_user()
        
        if data:
            user_id = data.user.id
            
            response = self.supabase.table('workouts').insert({
                'user_id':user_id,
                'name':name,
                'date' : date,
                'notes':notes,
            }).execute()
            
            return response
    
    def refresh(self):
        current_user = self.supabase.auth.get_user()

        if current_user:
            full_data = self.supabase.table('workouts').select("*").eq("user_id", current_user.user.id).execute()
            sanitized_data = full_data.data
            self.all_workouts = sanitized_data

    def delete_workout(self, id):    
        current_user = self.supabase.auth.get_user()

        if current_user:
            self.supabase.table('workouts').delete().eq("user_id", current_user.user.id).eq('id', id).execute()

    def edit_workout(self, id, name, date, notes):
        current_user = self.supabase.auth.get_user()

        if current_user:
            response = (
                self.supabase.table('workouts')
                .update({
                    'name' : name, 
                    'date' : date, 
                    'notes' : notes
                })
                .eq('user_id', current_user.user.id)
                .eq('id', id)
                .execute()
            )
             
    def sign_out(self):
        response = self.supabase.auth.sign_out()

class App():
    def __init__(self,page, app_connector) -> None:
        self.page :ft.Page = page
        self.app_connector = app_connector
        
        self.page.on_route_change = self.route_change
        
    def route_change(self, e = None):
        self.page.views.clear()
        self.app_connector.refresh()
        print('yea ok so we got this route:',self.page.route)
        new_view = Router.get_page(self.page.route, self.page, self.app_connector)
        self.page.views.append(new_view)
        self.page.update()
            
            

def main(page: ft.Page) -> None:
    supabase = init_database()
    page.route = '/auth'
    page.title = "Workout Logger"
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    
    
    app_connector = App_to_Backend_Connector(supabase=supabase)
    app_class = App(page,app_connector)
    
    app_class.route_change()
    
if __name__ == "__main__":
    ft.run(main=main, assets_dir='assets')