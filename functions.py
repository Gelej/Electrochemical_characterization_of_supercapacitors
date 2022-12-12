import matplotlib.pyplot as plt
import os
import originpro as op
import sys
import shutil


def get_data_from_file(file_name, offset_x=0.0):
    with open(file_name) as file_object:
        content = file_object.read()
    content_splitted = content.split()
    axis_x = content_splitted[1]
    axis_y = content_splitted[0]
    del content_splitted[0]
    del content_splitted[0]
    y = [float(content_splitted[i].replace(",", "."))
         for i in range(len(content_splitted)) if i % 2 == 0]
    x = [offset_x + float(content_splitted[i].replace(",", ".")) - float(content_splitted[0].replace(",", "."))
         for i in range(len(content_splitted)) if i % 2 != 0]
    while True:
        if y[-1] > y[-2]:
            del x[-1]
            del y[-1]
        else:
            break
    return x, y, axis_x, axis_y


def find_points_for_the_last_peak(x, y):
    len_x = len(x)
    for i in range(len_x-2, 1, -1):
        peak_x = x[i]
        peak_y = y[i]
        if peak_y > y[i-1] and peak_y > y[i+1]:
            under_peak_x = x[i + 1]
            under_peak_y = y[i + 1]
            last_point_x = x[len_x-1]
            last_point_y = y[len_x-1]
            print('Peak Y:', peak_y)
            print('Peak X:', peak_x)
            print('Under Peak Y:', under_peak_y)
            print('Under Peak X:', under_peak_x)
            print('Last Point Y:', last_point_y)
            print('Last Point X:', last_point_x)
            return peak_x, peak_y, under_peak_x, under_peak_y, last_point_x, last_point_y


def find_points_for_all_peaks(x, y):
    len_x = len(x)
    peak_x = []
    peak_y = []
    under_peak_x = []
    under_peak_y = []
    zero_point_x = []
    zero_point_y = []
    first_peak = True
    for i in range(len_x-2):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            if first_peak:
                first_peak = False
            else:
                peak_x.append(x[i])
                peak_y.append(y[i])
                under_peak_x.append(x[i + 1])
                under_peak_y.append(y[i + 1])
                for j in range(i, len_x-1):
                    if y[j] < y[j + 1]:
                        zero_point_x.append(x[j])
                        zero_point_y.append(y[j])
                        break
                    elif j == len_x-2:
                        zero_point_x.append(x[len_x-1])
                        zero_point_y.append(y[len_x-1])
    return peak_x, peak_y, under_peak_x, under_peak_y, zero_point_x, zero_point_y


def get_power(energy, delta_t):
    p = energy / delta_t
    print(f'P= {round(p, 2)} kW/kg')
    return p


def get_energy(csp, peak_y):
    e = (csp*pow(peak_y, 2))/(8*3.6)
    print(f'E= {round(e, 1)}Wh/kg')
    return e


def get_csp(J, zero_point_x, under_peak_x, under_peak_y, times=1):
    if times == 1:
        c_eff = (2 * float(J) * get_delta_t(zero_point_x, under_peak_x)) / under_peak_y
    else:
        c_eff = [(((2 * float(J) * get_delta_t(zero_point_x[i], under_peak_x[i])) / under_peak_y[i]) /
                  ((2 * float(J) * get_delta_t(zero_point_x[0], under_peak_x[0])) / under_peak_y[0])*100)
                 for i in range(times-1)]
    return c_eff


def get_delta_t(last_point_x, under_peak_x):
    return last_point_x - under_peak_x


def get_graph(x, y, axis_x, axis_y, points=(), title=''):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.scatter(x, y, s=50)
    for i in range(0, len(points), 2):
        ax.scatter(points[i], points[i+1], s=50)
    plt.suptitle(title)
    ax.set_ylabel(axis_y)
    ax.set_xlabel(axis_x)
    plt.show()


def filtering(data):
    data_filtered = [data[i] for i in range(len(data)-1)
                     if data[i + 1] >= data[i] <= data[i - 1] and data[i + 1] - 2 < data[i] > data[i - 1] - 2
                     or (data[i + 1] <= data[i] < data[i + 1] + 2 and data[i - 1] <= data[i] < data[i - 1] + 2)
                     or (data[i + 1] <= data[i] <= data[i - 1] and data[i + 1] + 2 > data[i] > data[i - 1] - 2)
                     or (data[i + 1] >= data[i] >= data[i - 1] and data[i + 1] - 2 < data[i] < data[i - 1] + 2)]
    return data_filtered


def get_files(path):
    offset_x = 0.0
    y = []
    x = []
    files = []
    for (path, dirs, data) in os.walk(path):
        for filename in data:
            print(filename)
            files.append(filename)
            file_data = (get_data_from_file(file_name=path + filename, offset_x=offset_x))
            x += [i for i in file_data[0]]
            y += [i for i in file_data[1]]
            offset_x = x[-1] + 1
            axis_x = file_data[2]
            axis_y = file_data[3]
    return x, y, axis_x, axis_y, files


def origin_shutdown_exception_hook(exctype, value, traceback):
    op.exit()
    sys.__excepthook__(exctype, value, traceback)


def push_data_to_origin(name, **data):

    if op and op.oext:
        sys.excepthook = origin_shutdown_exception_hook
    # Set Origin instance visibility.
    if op.oext:
        op.set_show(True)
    op.new()
    sheet = op.new_sheet('w')
    graph = op.new_graph(template='scatter')
    g = graph[0]
    i = 0
    for key, value in data.items():
        sheet.from_list(i, value, key)
        i = i + 1
#    g.add_plot(sheet, 1)
    op.save('D:\\Python\\data\\Done\\' + name + '.opju')
    # Exit running instance of Origin.
    if op.oext:
        op.exit()


def move_files_to_done_folder(path, files):
    for file in files:
        shutil.move(path + file, 'D:\\Python\\data\\Done')


def name_cut(file, prefix, suffix):
    filename = file.removeprefix(prefix)
    filename = filename.removesuffix(suffix)
    return filename
