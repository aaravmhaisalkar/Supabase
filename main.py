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
    def __init__(self, page: ft.Page, data) -> None:
        self.app_page = page
        self.data = data
       
        
        self.row_list = []
        
        
                
        for id, workout in enumerate(self.data, 1):
                self.row_list.append(
                    DataRow2(
                        cells=[
                            ft.DataCell(content=ft.Text(str(id))),
                            ft.DataCell(content=ft.Text(f'{workout['name']}')),
                            ft.DataCell(content=ft.Text(f'{workout['date']}')),
                            ft.DataCell(content=ft.Text(f'{workout['notes']}')),
                        ],
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

def check_session(supabase_client):
    api_response = supabase_client.auth.getSession()
    
    if api_response.session:
        return True
    return False
            
            

def delete_workout(supabase_client):
    check = check_session(supabase_client)
        
    if check == False:
        email = str(input("email: "))
        password = stdiomask.getpass(prompt="Enter Password: ")
        if len(password) < 6:
            return

        supabase_client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )
    
    
    current_user = supabase_client.auth.get_user()

    if current_user:
        full_data = supabase_client.table('workouts').select("*").eq("user_id", current_user.user.id).execute()
        workouts = full_data.data
        
        print("--- ALL WORKOUTS ---")
        if workouts:
            for index, workout in enumerate(workouts, 1):
                print(f'#{index} -  Name: {workout.get('name')} | Date: {workout.get('date')} | Notes: {workout.get('notes')}')
    
                    
        delete_workout_id = int(input("\n Delete what workout?"))
        
        if delete_workout_id > len(workouts):
            return
        
        else:
            index = delete_workout_id - 1
            
            workout_to_be_deleted = workouts[index].get('id')
            
            print(workout_to_be_deleted)
            
            supabase_client.table('workouts').delete().eq("user_id", current_user.user.id).eq('id', workout_to_be_deleted).execute()
            

def edit_workout(supabase_client):
    check = check_session(supabase_client=supabase_client)
            
    if check == False:
        email = str(input("email: "))
        password = stdiomask.getpass(prompt="Enter Password: ")
        if len(password) < 6:
            return

        
    
    
    current_user = supabase_client.auth.get_user()

    if current_user:
        full_data = supabase.table('workouts').select("*").eq("user_id", current_user.user.id).execute()
        workouts = full_data.data

        print("--- ALL WORKOUTS ---")
        if workouts:
            for index, workout in enumerate(workouts, 1):
                print(f"#{index} -  Name: {workout.get('name')} | Date: {workout.get('date')} | Notes: {workout.get('notes')}")

                    
        edit_workout_id = int(input("\nEdit what workout?"))

        if edit_workout_id > len(workouts):
            return

        else:
            editable = ('name', 'notes')
                    
            editing_stat = input("What stat to edit: ").lower().strip()
            
            if editing_stat not in editable:
                return
                    
            index = edit_workout_id - 1
            
            workout_to_be_edited = workouts[index].get('id')
            
            print(workout_to_be_edited)
            
            edited_value = input(f'Edit {editing_stat} to: ')
            
            if edited_value:
                response = (
                    supabase.table('workouts')
                    .update({editing_stat : edited_value})
                    .eq('user_id', current_user.user.id)
                    .eq('id', workout_to_be_edited)
                    .execute()
                )
                
                if response:
                    print(response)
                       
    
    
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
            content=Workouts_Table(page=self.app_page, data=self.app_connector.all_workouts)
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
            
class App_to_Backend_Connector():
    def __init__(self, supabase) -> None:
        self.supabase = supabase
        self.all_workouts = []
        
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
            full_data = self.supabase.table('workouts').select("name", "date", "notes").eq("user_id", current_user.user.id).execute()
            sanitized_data = full_data.data
            self.all_workouts = sanitized_data


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



