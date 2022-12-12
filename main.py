import functions as f

path = 'D:\\Python\\data\\ToDo\\'
file_data = f.get_files(path)
x = file_data[0]
y = file_data[1]
axis_x = file_data[2]
axis_y = file_data[3]
filenames = file_data[4]
print('Please choose one of the option:')
print('Enter 1 for calculate energy/power from last cycle of GCD')
print('Enter 2 for generate capacitance retention from GCD method')
select = input('Enter:')
if select == '1':
    points = f.find_points_for_the_last_peak(x, y)
    peak_x = points[0]
    peak_y = points[1]
    under_peak_x = points[2]
    under_peak_y = points[3]
    last_point_x = points[4]
    last_point_y = points[5]
    J = input('Please insert current density:')
    delta_t = f.get_delta_t(last_point_x, under_peak_x)
    delta_v = under_peak_y
    csp = f.get_csp(J, last_point_x, under_peak_x, under_peak_y)
    print(f'Csp= {round(csp)} F/g')
    energy = f.get_energy(csp, peak_y)
    power = f.get_power(energy, delta_t)
    f.get_graph(x, y, axis_x, axis_y, points)
elif select == '2':
    all_points = f.find_points_for_all_peaks(x, y)
    under_peak_x = all_points[2]
    under_peak_y = all_points[3]
    zero_point_x = all_points[4]
    J = input('Please insert current density:')
    c_eff = f.get_csp(J, zero_point_x, under_peak_x, under_peak_y, len(under_peak_x))
#    f.get_graph(range(1, len(c_eff)+1), c_eff, axis_x='cycle number', axis_y='capacitance retention [%]', title='Cycling stability')
    c_eff_filtered = f.filtering(c_eff)
#    f.get_graph(range(1, len(c_eff_filtered) + 1), c_eff_filtered, axis_x='cycle number', axis_y='capacitance retention [%]', title='Cycling stability')
    filename = f.name_cut(filenames[0], 'part01_', '.txt')
    f.push_data_to_origin(name=filename, capacitance_retention=c_eff, capacitance_retention_filtered=c_eff_filtered)
    f.move_files_to_done_folder(path, filenames)
else:
    print('Undefined select')
