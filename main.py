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
        self.date_selected_text = ft.Text(value="",size=15)
        
        self.date_picker = ft.DatePicker(
            last_date=self.today,
            on_change=self.date_picked,
        )

        
        super().__init__(
            width=300,
            height=50,
            padding=ft.Padding.all(8),
            border_radius=ft.BorderRadius.all(4),
            border=ft.Border.all(1, ft.Colors.BLACK),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.date_selected_text,
                    ft.Button(
                        width=140,
                        icon=ft.Icons.CALENDAR_MONTH, 
                        content="Pick Date", 
                        on_click=lambda _: self.app_page.show_dialog(self.date_picker)
                    )
                ]
            )
        )
    
    def date_picked(self, e):
        self.selected_date = e.control.value.strftime('%m/%d/%Y')
        self.date_selected_text.value = f'{self.selected_date}'

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
                            ft.DataCell(content=ft.Text(str(id))),
                            ft.DataCell(content=ft.Text(f'{workout['name']}')),
                            ft.DataCell(content=ft.Text(f'{workout['date']}')),
                            ft.DataCell(content=ft.Text(f'{workout['notes']}')),
                        ],
                        on_tap=handle_tap()
                    )
                )
        
        super().__init__(
            border=ft.Border.all(1, ft.Colors.BLACK),
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(5),
            content=Row(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    DataTable2(
                        width=1000,
                        columns=[
                            DataColumn2(size=DataColumnSize.S, label=ft.Text("#"), tooltip="Number", numeric=True),
                            DataColumn2(size=DataColumnSize.L, label=ft.Text("Opponent"), tooltip="Opponent"),
                            DataColumn2(size=DataColumnSize.L, label=ft.Text("Date"), tooltip="Date"),
                            DataColumn2(size=DataColumnSize.L, label=ft.Text("Notes"), tooltip="Notes"),
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
            'email' : ft.TextField(label='Email'),
            'password' : ft.TextField(label='Password', password=True, can_reveal_password=True),
            'checkbox' : ft.Checkbox(label="Check for sign-up (NOT sign-in)"),
            
        }
        
        self.error_bar = ft.Container(
            visible=False,
            width = 290,
            height=95,
            bgcolor=ft.Colors.RED_100,
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(10)
        )
        
        self.view = ft.View(
            padding= ft.Padding.all(5),
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                                alignment= ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("Sign In / Sign Up", size=25)
                                        ], 
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Divider(),
                                    *self.sign_up_controls.values(),
                                    ft.Button(content="Submit", width=145, height=35, bgcolor=ft.Colors.GREEN_200, color=ft.Colors.GREEN_700, on_click= lambda e: asyncio.create_task(self.check(e))),
                                    self.error_bar
                                ]
                            ),
                    padding=ft.Padding.all(15),
                    border=ft.Border.all(2,ft.Colors.BLACK),
                    border_radius=ft.BorderRadius.all(10)
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
                    padding= ft.Padding.all(5),
                    controls=[
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                        alignment= ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text("Home", size=25)
                                                ], 
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Divider(),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    Page_Switch_Button(page=self.app_page, route='/add'),
                                                    Page_Switch_Button(page=self.app_page, route='/all')
                                                ]
                                            )
                            
                                        ]
                                    ),
                            padding=ft.Padding.all(15),
                            border=ft.Border.all(2,ft.Colors.BLACK),
                            border_radius=ft.BorderRadius.all(10)
                        ),
                    ]
                )
                   
class Add_Workout():
    def __init__(self, page, app_connector) -> None:
        self.app_page = page
        self.app_connector :App_to_Backend_Connector = app_connector
        
        self.data = {}
        
        self.add_workout_inputs = {
            'name' : ft.TextField(label="Workout Name"),
            'date' : UniversalDateInput(page=self.app_page),
            'notes' : ft.TextField(label="Notes"),
        }
        
        self.error_bar = ft.Container(
            visible=False,
            width = 290,
            height=95,
            bgcolor=ft.Colors.RED_100,
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(10)
        )
        
        self.view = ft.View(
                    padding= ft.Padding.all(5),
                    controls=[
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                        alignment= ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text("Add", size=25)
                                                ], 
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Divider(),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    *self.add_workout_inputs.values(),
                                                    ft.Button(content="Add", on_click=lambda e: asyncio.create_task(self.add_workout(e))),
                                                    self.error_bar,
                                                    Page_Switch_Button(page=self.app_page, route='/home')
                                                ]
                                            )
                            
                                        ]
                                    ),
                            padding=ft.Padding.all(15),
                            border=ft.Border.all(2,ft.Colors.BLACK),
                            border_radius=ft.BorderRadius.all(10)
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
            self.error_bar.bgcolor = ft.Colors.GREEN_200
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
            content=Workouts_Table(page=self.app_page, data=self.app_connector.all_workouts, on_tap_function=self.go_to_workout_info)
        )
        
        self.view = ft.View(
                    padding= ft.Padding.all(5),
                    controls=[
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                        alignment= ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text("All Workouts", size=25)
                                                ], 
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Divider(),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    self.workouts,
                                                    Page_Switch_Button(page=self.app_page, route='/home')
                                                ]
                                            )
                            
                                        ]
                                    ),
                            padding=ft.Padding.all(15),
                            border=ft.Border.all(2,ft.Colors.BLACK),
                            border_radius=ft.BorderRadius.all(10)
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
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            workout['date'],
                            size=14,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Divider(),
                        ft.Text(
                            workout['notes'],
                            size=15
                        ),
                    ],
                    spacing=12
                )
            

        
        
        self.delete_button = ft.Button(
            content='Delete (long press)',
            on_long_press= lambda: self.delete_function()
        )
        
        self.edit_button = ft.Button(
            content='Edit',
            on_click= lambda: self.edit_function()
        )
        

       
        
        self.view = ft.View(
                    padding= ft.Padding.all(5),
                    controls=[
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                        alignment= ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            self.text,
                                            self.delete_button,
                                            self.edit_button,
                                            Page_Switch_Button(page=self.app_page, route='/all')
                                        ]
                                    ),
                            padding=ft.Padding.all(15),
                            border=ft.Border.all(2,ft.Colors.BLACK),
                            border_radius=ft.BorderRadius.all(10)
                        ),
                    ]
                )

          
    def delete_function(self):
        self.app_connector.delete_workout(self.app_connector.workout)
        self.app_connector.workout = ''
        
        self.text.controls = [ft.Text("Deleted")]
        self.delete_button.visible = False
    
    def edit_function(self):
        for workout in self.app_connector.all_workouts:
            if workout['id'] == self.app_connector.workout:
                self.name_field = ft.TextField(
                    label="Name",
                    value=workout['name']
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
                    min_lines=3
                )

                self.text.controls = [
                    self.name_field,
                    self.date_field,
                    self.notes_field,
                ]
                
                self.submit_edits = ft.Button(
                    content='Save',
                    on_click=lambda: asyncio.create_task(self.submit_button_on_click())
                )

        self.view.controls = [
            self.text,
            self.submit_edits,
            Page_Switch_Button(page=self.app_page, route='/all')
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
    page.theme_mode = ft.ThemeMode.LIGHT
    
    
    app_connector = App_to_Backend_Connector(supabase=supabase)
    app_class = App(page,app_connector)
    
    app_class.route_change()
    
if __name__ == "__main__":
    ft.run(main=main, assets_dir='assets')



