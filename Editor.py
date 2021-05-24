import importlib.util
import os
import pickle
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from tkinter import colorchooser

from PIL import ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import Commands.BasicOperationCommands as BasicOperations
import Commands.CommandHistory as CommandHistory
import Commands.ApplyEffectCommand as ApplyEffectCommand
from Canvas import *

MAX_HISTORY_STACK = 10


def getFiles():
    this_dir = os.path.dirname(__file__) + "\Effects"
    files = []
    for r, d, f in os.walk(this_dir):
        for file in f:
            if file.endswith(".py"):
                name, path = (file.removesuffix(".py"), os.path.join(r, file))
                files.append((name, path))
    return files


def importEffects():
    files = getFiles()
    effects = []
    for effect in files:
        spec = importlib.util.spec_from_file_location(effect[0], effect[1])
        module = importlib.util.module_from_spec(spec)
        effects.append(module)
        spec.loader.exec_module(module)
    return effects


def calculateCanvasSize(canvas_width, canvas_height, img_width, img_height):
    if canvas_height < canvas_width:
        resize_width = round((canvas_height / img_height) * img_width)
        resize_height = canvas_height
    else:
        resize_height = round((canvas_width / img_width) * img_height)
        resize_width = canvas_width
    # DO SOME MORE MATH HERE LATER#
    while resize_width > canvas_width or resize_height > canvas_height:
        resize_width = round(resize_width * 80 / 100)
        resize_height = round(resize_height * 80 / 100)
    return resize_width, resize_height


def set_text(e, text):
    e.delete(0, END)
    e.insert(0, text)
    return


class Editor:
    def __init__(self):
        self.canvas_history = []
        self.canvas_list = []
        self.icons_list = []
        self.selected_canvas_index = 0
        self.selected_layer_index = 0

        self.root = Tk()
        self.root.title("S.I.P.E")
        self.root.iconbitmap("img/icon.ico")
        self.root.minsize(640, 640)

        ########CREATE  MENU BAR########
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.createNewCanvasWindow)
        file_menu.add_command(label="Open file", command=self.createCanvasFromImage)
        file_menu.add_command(label="Import file", command=self.openImage)
        file_menu.add_command(label="Save", command=self.saveImageToFile)
        file_menu.add_separator()
        file_menu.add_command(label="Open project", command=self.loadCanvas)
        file_menu.add_command(label="Save project", command=self.saveCanvas)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_separator()
        edit_menu.add_command(label="next Canvas", command=self.nextCanvas)
        edit_menu.add_command(label="previous Canvas", command=self.previousCanvas)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        layer_menu = Menu(menu_bar, tearoff=0)
        layer_menu.add_command(label="Create new Layer", command=self.newLayerWindow)
        layer_menu.add_command(label="Change Name", command=self.renameLayerWindow)
        layer_menu.add_command(label="Duplicate", command=lambda: self.executeCommand(BasicOperations.DuplicateLayerCommand(self)))
        menu_bar.add_cascade(label="Layer", menu=layer_menu)

        effects_menu = Menu(menu_bar, tearoff=0)
        self.files = getFiles()
        for i in range(0, len(self.files)):
            effect_name = self.files[i][0]
            effects_menu.add_command(label=effect_name, command=lambda bound_i=i: self.runEffect(bound_i))
        menu_bar.add_cascade(label="Effects", menu=effects_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About...", command=self.AboutProgramWindow)
        help_menu.add_command(label="Author", command=self.AboutAuthor)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)
        ########END OF MENU BAR########

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=2)

        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        self.preview_frame = Frame(self.root, background="grey")
        self.preview_frame.grid(column=0, row=0, columnspan=2, rowspan=3, sticky="nswe")
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        self.canvas_composition = Label(self.preview_frame, text='None', background="grey")
        self.canvas_composition.grid(sticky="nswe", column=0, row=0)

        self.composition_image = None

        self.canvas_composition.bind('<Configure>', self._resize_event)

        self.analysis_frame = Frame(self.root, highlightbackground="black", highlightthickness=2)
        self.analysis_frame.grid(column=2, row=0, sticky="nswe")
        self.analysis_frame.columnconfigure(0, weight=1)

        self.layer_control_frame = Frame(self.root, highlightbackground="black", highlightthickness=2)
        self.layer_control_frame.grid(column=2, row=1, sticky="nswe")
        for i in range(0, 4):
            self.layer_control_frame.columnconfigure(i, weight=1)
            self.layer_control_frame.rowconfigure(i, weight=1)
        Label(self.layer_control_frame, text="Layer Control").grid(column=0, row=0, columnspan=4)

        Label(self.layer_control_frame, text="Position x:").grid(column=0, row=1)
        self.input_layer_x = Entry(self.layer_control_frame)
        self.input_layer_x.grid(column=1, row=1)
        Label(self.layer_control_frame, text="y:").grid(column=2, row=1)
        self.input_layer_y = Entry(self.layer_control_frame)
        self.input_layer_y.grid(column=3, row=1)
        self.apply_layer_scale = Button(self.layer_control_frame, text="Apply", command=lambda: self.executeCommand(
            BasicOperations.ChangeLayerPositionCommand(self, int(self.input_layer_x.get()),
                                                       int(self.input_layer_y.get()))))
        self.apply_layer_scale.grid(column=4, row=1)

        Label(self.layer_control_frame, text="Scale width:").grid(column=0, row=2)
        self.input_layer_width = Entry(self.layer_control_frame)
        self.input_layer_width.grid(column=1, row=2)
        Label(self.layer_control_frame, text="height:").grid(column=2, row=2)
        self.input_layer_height = Entry(self.layer_control_frame)
        self.input_layer_height.grid(column=3, row=2)
        self.apply_layer_scale = Button(self.layer_control_frame, text="Apply", command=lambda: self.executeCommand(
            BasicOperations.ChangeLayerScaleCommand(self, int(self.input_layer_width.get()),
                                                    int(self.input_layer_height.get()))))
        self.apply_layer_scale.grid(column=4, row=2)

        Label(self.layer_control_frame, text="Rotation:").grid(column=1, row=3)
        self.input_layer_rotation = Entry(self.layer_control_frame)
        self.input_layer_rotation.grid(column=2, row=3)
        self.apply_layer_rotation = Button(self.layer_control_frame, text="Apply", command=lambda: self.executeCommand(
            BasicOperations.ChangeLayerRotationCommand(self, int(self.input_layer_rotation.get()))))
        self.apply_layer_rotation.grid(column=3, row=3)



        self.layers_frame = Frame(self.root, highlightbackground="black", highlightthickness=2)
        self.layers_frame.grid(column=2, row=2, sticky='nswe')
        self.layers_list = Frame(self.layers_frame)
        Label(self.layers_frame, text="Mode:").grid(column=0, row=0)
        self.OPTIONS = ["Normal", "Darker", "Multiply", "Add", "Lighter"]
        self.mode_variable = StringVar(self.layers_frame)
        self.mode_variable.set(self.OPTIONS[0])
        drop_down_mode = OptionMenu(self.layers_frame, self.mode_variable, *self.OPTIONS,
                                    command=lambda value: self.executeCommand(
                                        BasicOperations.ChangeLayerModeCommand(self, self.OPTIONS.index(str(value)))))
        drop_down_mode.grid(column=1, row=0)
        Label(self.layers_frame, text="Layers: ").grid(column=0, row=1)
        self.layers_list.grid(column=0, row=2, columnspan=4)
        self.layers_tree = ttk.Treeview(self.layers_list)
        self.layers_buttons = Frame(self.layers_frame)
        self.layers_buttons.rowconfigure(0, weight=1)
        self.layers_buttons.columnconfigure(0, weight=1)
        self.layers_buttons.columnconfigure(1, weight=1)
        self.layers_buttons.columnconfigure(2, weight=1)
        self.layers_buttons.columnconfigure(3, weight=1)

        Button(self.layers_buttons, text="+",
               command=self.newLayerWindow).grid(column=0, row=0)
        Button(self.layers_buttons, text="-",
               command=lambda: self.executeCommand(BasicOperations.DeleteLayerCommand(self))).grid(column=1, row=0)
        Button(self.layers_buttons, text="^",
               command=lambda: self.executeCommand(BasicOperations.MoveLayerUpCommand(self))).grid(column=2, row=0)
        Button(self.layers_buttons, text="v",
               command=lambda: self.executeCommand(BasicOperations.MoveLayerDownCommand(self))).grid(column=3, row=0)
        self.layers_buttons.grid(column=0, row=3, columnspan=4, sticky="nswe")

        self.root.bind('<Control-z>', self.undo)

        self.root.mainloop()

    ###ABOUT AND HELP WINDOWS###
    def AboutProgramWindow(self):
        about_window = Toplevel(self.root)
        about_window.columnconfigure(0, weight=1)
        about_window.rowconfigure(0, weight=1)
        about_window.title("About Program")
        Label(about_window, text="S.I.P.E	- Simple Image Python Editor is a self-development application made for \n"
                                 "<'Scripting Languages'> course on University. Main idea of this program is to provide"
                                 " \nsimple yet effective tools to edit images. Program is written in Python "
                                 "3.9.1.").grid(column=0, row=0)
        Button(about_window, text="OK", command=about_window.destroy).grid(column=0, row=1)

    def AboutAuthor(self):
        about_window = Toplevel(self.root)
        about_window.columnconfigure(0, weight=1)
        about_window.rowconfigure(0, weight=1)
        about_window.rowconfigure(1, weight=1)
        about_window.rowconfigure(2, weight=1)
        about_window.title("About Author")
        Label(about_window, text="Hello, I'm Mateusz Majdowski. I'm a Computer Science student and \n["
                                 "part-time] motion-designer. Computer Graphics is my BIG hobby that's why i decided\n"
                                 "to give it a shot and wrote simple photo editor.\n\n").grid(column=0, row=0)
        contact = Text(about_window, height=1, width=34)
        contact.insert(1.0, "Contact: 246715@student.pwr.edu.pl")
        contact.configure(bg=about_window.cget('bg'), relief="flat")
        contact.configure(state="disabled")
        contact.grid(column=0, row=1)

        Button(about_window, text="OK", command=about_window.destroy).grid(column=0, row=2)

    ###UI UPDATES###
    def updateAll(self):
        self.updateCanvas()
        self.updateHistogram()
        self.updateTransformFrame()
        self.updateLayersFrame()

    def updateCanvas(self):
        self.composition_image = self.canvas_list[self.selected_canvas_index].getPreview()
        self.resize_canvas(self.preview_frame.winfo_width(), self.preview_frame.winfo_height())
        self.showLayers()
        self.createHistogram()

    def updateHistogram(self):
        self.createHistogram()

    def updateLayersFrame(self):
        self.showLayers()

    def updateTransformFrame(self):
        layer = self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index]
        set_text(self.input_layer_height, str(layer.height))
        set_text(self.input_layer_width, str(layer.width))
        set_text(self.input_layer_y, str(round(layer.position_y)))
        set_text(self.input_layer_x, str(round(layer.position_x)))
        set_text(self.input_layer_rotation, str(round(layer.rotation)))

    def showLayers(self):
        for widget in self.layers_list.winfo_children():
            widget.destroy()
        self.icons_list.clear()
        self.layers_tree = ttk.Treeview(self.layers_list, show="tree")
        self.layers_tree.bind("<<TreeviewSelect>>", self.updateLayersView)
        style = ttk.Style(self.layers_list)
        style.configure('Treeview', rowheight=38)
        index = 0
        length = len(self.canvas_list[self.selected_canvas_index].layers_list) - 1
        for layer in self.canvas_list[self.selected_canvas_index].layers_list:
            layer_name = layer.getName()
            self.icons_list.append(layer.getIcon())
            self.layers_tree.insert('', 0, text=layer_name, image=self.icons_list[len(self.icons_list) - 1])
            index += 1
        #self.layers_tree.selection_set(self.layers_tree.get_children()[length - self.selected_layer_index])
        self.layers_tree.grid(column=0, row=0, sticky="nwse")

    def resize_canvas(self, new_width, new_height):
        img_width, img_height = self.composition_image.size
        resize_width, resize_height = calculateCanvasSize(new_width, new_height, img_width, img_height)
        img = ImageTk.PhotoImage(image=self.composition_image.resize((resize_width, resize_height)))
        self.canvas_composition.text = ""
        self.canvas_composition.configure(image=img)
        self.canvas_composition.image = img

    def _resize_event(self, event):
        if self.composition_image is not None:
            canvas_width = event.width
            canvas_height = event.height
            self.resize_canvas(canvas_width, canvas_height)

    def updateLayersView(self, event):
        index = self.layers_tree.index(self.layers_tree.focus())
        self.selected_layer_index = len(self.canvas_list[self.selected_canvas_index].layers_list) - index - 1
        self.mode_variable.set(self.OPTIONS[self.canvas_list[self.selected_canvas_index].layers_list[
                                                self.selected_layer_index].mode.value - 1])

    def createHistogram(self):
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        figure = plt.Figure(figsize=(4, 2), dpi=50)
        figure.suptitle("Histogram")
        chart_type = FigureCanvasTkAgg(figure, self.analysis_frame)
        chart_type.get_tk_widget().grid(column=0, row=0, sticky="nwse")

        p = figure.gca()
        bw_img = np.array(self.composition_image.convert('L'), dtype=int)
        color = ('r', 'g', 'b')
        for i, col in enumerate(color):
            hist, bins = np.histogram(np.array(self.composition_image)[:, :, i], 256, [0, 256])
            p.plot(hist, color=col)

        hist, bins = np.histogram(bw_img, 256, [0, 256])
        p.plot(hist, color="black")

    def nextCanvas(self):
        if len(self.canvas_list)-1 >self.selected_canvas_index:
            self.selected_canvas_index +=1
            self.updateAll()

    def previousCanvas(self):
        if self.selected_canvas_index>0:
            self.selected_canvas_index -=1
            self.updateAll()

    ###Layers Editing###
    def runEffect(self, value):
        self.executeCommand(ApplyEffectCommand.RenderEffectCommand(self,self.files[value][0], self.files[value][1]))

    def addNewLayer(self, r, g, b):
        self.executeCommand(BasicOperations.NewLayerCommand(self, r, g, b))
        self.updateAll()

    def newLayerWindow(self):
        new_color = colorchooser.askcolor()
        if new_color:
            self.addNewLayer(new_color[0][0], new_color[0][1], new_color[0][2])

    def renameLayer(self, window, new_name):
        if window is not None:
            window.destroy()
        self.executeCommand(BasicOperations.RenameLayerCommand(self, new_name))

    def renameLayerWindow(self):
        layer_conf_window = Toplevel(self.root)
        layer_conf_window.title("Rename Layer")
        Label(layer_conf_window, text="Name: ").grid(column=0, row=0)
        layer_name = Entry(layer_conf_window, text="Untitled")
        layer_name.grid(column=1, row=0)
        Button(layer_conf_window, text="OK",
               command=lambda: self.renameLayer(layer_conf_window, layer_name.get())).grid(column=0, row=1)
        Button(layer_conf_window, text="Cancel", command=layer_conf_window.destroy).grid(column=1, row=1)

    def deleteLayer(self):
        if len(self.canvas_list[self.selected_canvas_index].layers_list) > 1:
            del self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index]
            if self.selected_layer_index > 0:
                self.selected_layer_index -= 1

    def moveLayerUp(self):
        if self.selected_layer_index < len(self.canvas_list[self.selected_canvas_index].layers_list) - 1:
            temp = self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index]
            self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index] = \
                self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index + 1]
            self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index + 1] = temp
            self.selected_layer_index += 1

    def moveLayerDown(self):
        if self.selected_layer_index >= 1:
            temp = self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index]
            self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index] = \
                self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index - 1]
            self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index - 1] = temp
            self.selected_layer_index -= 1
    '''
    def changeLayerPosition(self):
        if self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index].setPosition(
                int(self.input_layer_x.get()), int(self.input_layer_y.get())):
            self.updateAll()

    def changeLayerScale(self):
        if (self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index].setScale(
                int(self.input_layer_width.get()), int(self.input_layer_height.get()))):
            self.updateAll()
    '''
    def openImage(self):
        file_path = filedialog.askopenfilename(title="Select file",
                                               filetypes=(
                                                   ("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                   ("all files", "*.*")))
        if not file_path:
            return
        layer_name = os.path.basename(file_path)
        new_img = Image.open(file_path)
        self.executeCommand(BasicOperations.OpenImageCommand(self, layer_name, new_img))

    def setMode(self, value):
        self.canvas_list[self.selected_canvas_index].layers_list[self.selected_layer_index].setMode(value + 1)

    ###CREATE NEW CANVAS###
    def createNewCanvas(self, window, canvas_name, canvas_width, canvas_height):
        if window is not None:
            window.destroy()
        self.canvas_list.append(Canvas(canvas_name, width=canvas_width, height=canvas_height))
        self.canvas_history.append(CommandHistory.CommandHistory(MAX_HISTORY_STACK))
        self.composition_image = self.canvas_list[0].getPreview()
        self.selected_canvas_index = len(self.canvas_list) - 1
        self.updateAll()

    def createNewCanvasWindow(self):
        canvas_conf_window = Toplevel(self.root)
        canvas_conf_window.title("Create new Canvas")
        Label(canvas_conf_window, text="Name: ").grid(column=0, row=0)
        canvas_name = Entry(canvas_conf_window, text="Untitled")
        canvas_name.grid(column=1, row=0)
        Label(canvas_conf_window, text="Width: ").grid(column=0, row=1)
        canvas_width = Entry(canvas_conf_window)
        canvas_width.grid(column=1, row=1)
        Label(canvas_conf_window, text="Height: ").grid(column=0, row=2)
        canvas_height = Entry(canvas_conf_window)
        canvas_height.grid(column=1, row=2)
        Button(canvas_conf_window, text="OK",
               command=lambda: self.createNewCanvas(canvas_conf_window, canvas_name.get(), int(canvas_width.get()),
                                                    int(canvas_height.get()))).grid(column=0, row=3)
        Button(canvas_conf_window, text="Cancel", command=canvas_conf_window.destroy).grid(column=1, row=3)


    def createCanvasFromImage(self):
        file_path = filedialog.askopenfilename(title="Select file",
                                               filetypes=(
                                                   ("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                   ("all files", "*.*")))
        if not file_path:
            return
        print(file_path)
        canvas_name = os.path.basename(file_path)
        new_img = Image.open(file_path)
        img_width, img_height = new_img.size
        self.canvas_list.append(Canvas(canvas_name, new_img, img_width, img_height))
        self.canvas_history.append(CommandHistory.CommandHistory(MAX_HISTORY_STACK))
        self.selected_canvas_index = len(self.canvas_list) - 1
        self.updateAll()

    def isCanvasSelected(self):
        if len(self.canvas_list) > 0 and self.selected_canvas_index > 0:
            return True
        else:
            return False

    ###COMMAND PATTERN FUNCTIONS###
    def executeCommand(self, command):
        if command.execute():
            self.canvas_history[self.selected_canvas_index].push(command)
        self.updateAll()

    def undo(self, event):
        print("Undo")
        if not self.canvas_history[self.selected_canvas_index].isEmpty():
            command = self.canvas_history[self.selected_canvas_index].pop()
            if command is not None:
                command.undo()
                self.selected_layer_index = max(0, min(self.selected_layer_index, len(
                    self.canvas_list[self.selected_canvas_index].layers_list) - 1))
                self.updateAll()

    ###SAVE AND LOAD OPTIONS###
    def saveImageToFile(self):
        ftypes = [('JPEG File', '*.jpg'), ('PNG File', '*.png')]
        filename = filedialog.asksaveasfilename(title="Save file", filetypes=ftypes, defaultextension='.jpg')
        if filename:

            print(filename)
            img = self.canvas_list[self.selected_canvas_index].getFinalImage()
            if filename[-3:] == "jpg":
                img = img.convert("RGB")
            img.save(filename)

    def loadCanvas(self):
        filename = filedialog.askopenfilename(title="Select file", filetypes=[("Pickle File", "*.p")])
        if filename:
            print("saved!")
            self.canvas_list.append(pickle.load(open(filename, "rb")))
            self.selected_canvas_index = len(self.canvas_list) - 1
            self.canvas_history.append(CommandHistory.CommandHistory(MAX_HISTORY_STACK))
            self.updateAll()

    def saveCanvas(self):
        filename = filedialog.asksaveasfilename(title="Save file", filetypes=[("Pickle File", "*.p")],
                                                defaultextension='.p')
        if filename:
            print("saved!")
            pickle.dump(self.canvas_list[self.selected_canvas_index], open(filename, "wb"))
