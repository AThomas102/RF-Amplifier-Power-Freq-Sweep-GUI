
def importer(filename, hlines):
    import csv

    with open(str(filename), newline='') as datafile:
        data = list(csv.reader(datafile))
        
    headers = data[0:hlines]
    
    del data[0:hlines]
    
    return data, headers

""""""""""""""""""""""""""""""""""""""""""""

def blank_delete(data):
    data_noblank = []
    counter = 0
    for i in range(len(data)):
        row = data[i]
        voltage = row[-1]
        if voltage != str(''):
            row[10] = 1000*float(row[10])
            row[11] = 1000*float(row[11])
            row[12] = 1000*float(row[12])
            data_noblank.append(row)
        else:
            counter+=1
    
    percent_blank = round(100*counter/len(data),2)
    percent_blank = str(percent_blank) + "%"
    return data_noblank, counter, percent_blank

""""""""""""""""""""""""""""""""""""""""""""
def time_to_int(time):
    time = time.split(":")
    time = int(time[0]) + int(time[1])/60 + int(time[2])/3600
    
    return time

""""""""""""""""""""""""""""""""""""""""""""

def time_to_string(time):
    import numpy as np
    time = str(time)
    time = time.split(".")
    
    # if len(time[0]) == 1:
    #     hrs = "0" + time[0]
        
    # else:
        #hrs = str(time[0])
   
    hrs = str(time[0])
    
    mins = str(60*float("0." + time[1]))
    
    mins = mins.split(".")
    
    secs = mins[1]

    mins = mins[0]
    
    if len(mins) == 1:
        mins = "0" + mins
        
    if secs != "0":
        secs = str(int(np.round(60*float("0." + secs),2)))
            
        if secs == str(60):
            secs = "00"
            mins = str(int(mins) + 1)
    
    if len(secs) == 1:
        secs = "0" + secs
            
    time = str(hrs) + ":" + str(mins) + ":" + str(secs)
    
    return time

""""""""""""""""""""""""""""""""""""""""""""

def temp_cycling(data_noblank, test_temp, temp_threshold):
    
    time_col=[]
    temperature_col = []
    for i in range(len(data_noblank)):
        row = data_noblank[i]
        time = row[2]
   
        time = time_to_int(time)
        time_col.append(time)
        
        temperature = float(row[9])
        temperature_col.append(temperature)
        
    import matplotlib.pyplot as plt
    
    plt.plot(time_col, temperature_col)
    plt.xlabel('Time (h)')
    plt.ylabel('Temperature (°C)')
    plt.grid()
    plt.show()
    
    import numpy as np
    
    roundedtemps = []
    for i in range(len(temperature_col)):
        temperature = round(temperature_col[i],1)
        roundedtemps.append(temperature)
    
    uniquetemps = np.unique(roundedtemps)
    uniquetemps = uniquetemps.tolist()
    
    frequencies = []
    for i in range(len(uniquetemps)):
        frequency = roundedtemps.count(uniquetemps[i])
        frequencies.append(frequency)
        
    plt.bar(uniquetemps,frequencies, width = 0.1, edgecolor = 'black')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Frequency')
    plt.grid()
    plt.show()
    
    plt.bar(uniquetemps,frequencies, width = 0.1, edgecolor = 'black')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Frequency')
    plt.grid()
    plt.xlim(test_temp - 5, test_temp + 5)
    plt.axvline(x = test_temp - temp_threshold*test_temp/100, color = 'red', linestyle = '--')
    plt.axvline(x = test_temp + temp_threshold*test_temp/100, color = 'red', linestyle = '--')
    plt.show()
    
    return 

""""""""""""""""""""""""""""""""""""""""""""

def soak_remove(data, test_temp, temp_threshold):
    import numpy as np
    
    test_data = [i for i in data]
    soak_data = []
    soak_indices = []
    
    for i in range(len(data)):
        row = data[i]
        temperature = float(row[9])
        temp_var = 100*np.abs(temperature-test_temp)/test_temp
        if temp_var > temp_threshold:
            soak_data.append(row)
            soak_indices.append(i)

    soak_indices = sorted(soak_indices, reverse = True)
    
    for i in range(len(soak_indices)):
        for j in range(len(test_data)):
            if soak_indices[i] == j:
                del(test_data[j])
                break
    
    return test_data, soak_data

""""""""""""""""""""""""""""""""""""""""""

def device_detect(data,devcolnum):
    import numpy as np
    device_col = []
    for i in range(len(data)):
        row = data[i]
        device = int(float((row[devcolnum])))
        device_col.append(device)
    
    devices = np.unique(device_col)
    devices = devices.tolist()

    return devices

""""""""""""""""""""""""""""""""""""""""""""

def device_split(data,devices,devcolnum):

    data_devices = []
    for i in range(len(devices)):
        data_devices.append([])
        for j in range(len(data)):
            row = data[j]
            if int(float(row[devcolnum])) == devices[i]:
                data_devices[i].append(row)
    
    return data_devices

""""""""""""""""""""""""""""""""""""""""""""

def plot_all_1(data_devices, devices):
            
    times = []
    currents = []
    powers = []
    for i in range(len(data_devices)):
        device = data_devices[i]
        times.append([])
        currents.append([])
        powers.append([])
        for j in range(len(device)):
            row = device[j]
            
            time = row[2]
            time = time_to_int(time)
            
            current = float(row[10])
            power = float(row[12])
            
            times[i].append(time)
            currents[i].append(current)
            powers[i].append(power)
     

    return times, currents, powers

""""""""""""""""""""""""""""""""""""""""""""

def tc_split(test_data_devices, spot_time):
    
    time_col=[]
    for i in range(len(test_data_devices)):
        device = test_data_devices[i]
        time_col.append([])
        for j in range(len(device)):
            row = device[j]
            time = row[2]
            time = time_to_int(time)
            time_col[i].append(time)
    
    intervals = []
    indices = []

    for i in range(len(time_col)):
        device = time_col[i]
        intervals.append([])
        indices.append([])
        indices[i].append(0)
        for j in range(len(device)-1):
            interval = device[j+1]-device[j]
            intervals[i].append(interval)
            if interval > 5*spot_time/60:
                indices[i].append(j+1)
    
    test_cycles = []
    
    if len(indices[0])>1:
        for i in range(len(indices)):
            device_index = indices[i]
            device = test_data_devices[i]
            test_cycles.append([])
            for j in range(len(device_index)-1):
                test_cycles[i].append([])
                tc = test_cycles[i]
                for k in range(device_index[j],device_index[j+1]):
                    tc[j].append(device[k])
    else:
        for i in range(len(test_data_devices)):
            device = test_data_devices[i]
            test_cycles.append([device])
            

    return time_col, indices, test_cycles

""""""""""""""""""""""""""""""""""""""""""""

def tc_length(test_devices_cycles):
    
    import numpy as np
    
    lengths = []
    for i in range(len(test_devices_cycles)):
        device = test_devices_cycles[i]
        lengths.append([])
        for j in range(len(device)):
            tc = device[j]
            length = len(tc)
            lengths[i].append(length)
    
    dev1 = lengths[0]
    sortedlengths = sorted(dev1)
    uniquelengths = np.unique(sortedlengths)
    uniquelengths = uniquelengths.tolist()
        
    lengthfrequencies = []
    for i in range(len(uniquelengths)):
        length = uniquelengths[i]
        frequency = dev1.count(length)
        lengthfrequencies.append(frequency)
       
    return lengths, uniquelengths, lengthfrequencies

""""""""""""""""""""""""""""""""""""""""""""

def time_function(time_col, indices):
    
    if len(indices[0]) > 1:
        soak_times = []
        for i in range(len(time_col)):
            cycle_durations = []
            end = []
            
            device_time = time_col[i]
            device_indices = indices[i]
            for j in range(len(device_indices)-1):
                index1 = device_indices[j]
                index2 = device_indices[j+1] - 1
                cycle_start = device_time[index1]
                cycle_end = device_time[index2]
                end.append(cycle_end)
    
                cycle_duration = cycle_end - cycle_start
                cycle_durations.append(cycle_duration)
            
            cumulative_durations = []
            cumulative_durations.append(cycle_durations[0])
            for i in range(1,len(cycle_durations)):
                cumulative_duration =  cycle_durations[i] + cumulative_durations[i-1]
                cumulative_durations.append(cumulative_duration)
    
            device_soak_times = []
            for i in range(len(cumulative_durations)):
                soak_time = end[i] - cumulative_durations[i]
                device_soak_times.append(soak_time)
            
            soak_times.append(device_soak_times)
    else:
        soak_times = [[0] for i in indices]
        
    return soak_times

""""""""""""""""""""""""""""""""""""""""""""
def averager(tc,threshold):
    import numpy as np
    
    B = [i for i in tc]                                              #make a copy
    if len(tc) > 0:

        deleted = []                                    #list to store deleted info
        counter = 0                                     #counter for while loop
        while counter < len(tc)+1:                      #counter starts at 0, so add 1 to loop n times if n is the number of spot scans in the test cycle
            counter +=1                                 #add 1 to counter    
            Errors = []                                 #list to store errors
            for i in range(len(B)):                     #loop over each value in copy of test cycle. Copy will get shorter, so we use copy here instead of original
                avg = np.average(B)                     #find average of the spot scans
                Error = np.abs(B[i]-avg)/avg            #find errors of the spot scans
                Errors.append(Error)                    #and append to errors list
            
            if max(Errors) > threshold/100:             #if the maximum error is greater than the threshold
                j = Errors.index(max(Errors))           #j is the index corresponding to the maximum error
                k = tc.index(B[j])
                deleted.append(k)                       #append the index, the spot scan with the maximum error, and the maximum error itself     
                del(B[j])                               #and then delete the spot scan with the maximum error from the copy of the test cycle. Since this is a while loop, it will now repeat the average and delete the maximum etc until counter = number of spot scans
            else:
                break

        average = np.average(B)                         #one while loop is finished, average the copy
    
    else:
        average = np.average(B)
        deleted = []
    
    return average, deleted                      #return the average, the shortened test cycle, and the deleted info

""""""""""""""""""""""""""""""""""""""""""""
def statistics(mode, test_cycles, soak_times, avging_threshold, constant_set, tolerance):
    from analysis_module import averager
    import numpy as np
    averages = []  
    
    for i in range(len(test_cycles)):
        device = test_cycles[i]
        soak_time = soak_times[i]
        averages.append([])
        
        for j in range(len(device)):
            counter_cycles = 0
            counter_tol = 0
            counter_avging = 0
            time = soak_time[j]
            tc = device[j]
            currents = []
            powers = []
            voltages = []
            temperatures = []
            photocurrents = []
            devs = []
            timestamps = []
            
            for k in range(len(tc)):
                
                spotscan = tc[k]
        
                current = float(spotscan[10])
                power = float(spotscan[12])
                voltage = float(spotscan[13])
                photocurrent = float(spotscan[11])
                temperature = float(spotscan[9])
                timestamp = str(spotscan[3])
                
                if mode == str("APC"):
                    
                    if 100*np.abs(power-constant_set)/constant_set <= tolerance:
                        currents.append(current)
                        powers.append(power)
                        voltages.append(voltage)
                        temperatures.append(temperature)
                        photocurrents.append(photocurrent)
                        devs.append(int(spotscan[4]))
                        timestamps.append(timestamp)
                    
                    else:
                        counter_tol += 1
                                                
                if mode == str("ACC"):
                   
                    if 100*np.abs(current-constant_set)/constant_set <= tolerance:
                        currents.append(current)
                        powers.append(power)
                        voltages.append(voltage)
                        temperatures.append(temperature)
                        photocurrents.append(photocurrent)
                        devs.append(int(spotscan[4]))
                        timestamps.append(timestamp)
                    
                    else:
                        counter_tol += 1
                
            if mode == str("APC"):
                
                degrading, deleted = averager(currents,avging_threshold)
                counter_avging += len(deleted)
                deleted = sorted(deleted,reverse=True)
                
                for l in deleted:
                    del(powers[l])
                    del(voltages[l])
                    del(temperatures[l])
                    del(photocurrents[l])
                    del(devs[l])
                    del(timestamps[l])
                
                constant = np.mean(powers)
                voltage = np.mean(voltages)
                temperature = np.mean(temperatures)
                photocurrent = np.mean(photocurrents)
                dev = np.mean(devs)             
                
                if len(timestamps)>0:
                    timestamp = timestamps[0]
                else:
                    timestamp = ""
                    
                if dev > -1:            
                    averages[i].append([time, timestamp, dev, temperature, degrading, photocurrent, constant, voltage, counter_tol, counter_avging, counter_cycles])
    
                else:
                    counter_cycles+=1
                
            if mode == str("ACC"):
            
                degrading, deleted = averager(powers,avging_threshold)
                counter_avging += len(deleted)
                deleted = sorted(deleted,reverse=True)
                
                for l in deleted:
                    del(currents[l])
                    del(voltages[l])
                    del(temperatures[l])
                    del(photocurrents[l])
                    del(devs[l])
                    del(timestamps[l])
                    
                constant = np.mean(currents)
                voltage = np.mean(voltages)
                temperature = np.mean(temperatures)
                photocurrent = np.mean(photocurrents)
                dev = np.mean(devs)
                
                if len(timestamps)>0:
                    timestamp = timestamps[0]
                else:
                    timestamp = ""
                
                if dev > -1:    
                    averages[i].append([time, timestamp, dev, temperature, constant, photocurrent, degrading, voltage, counter_tol, counter_avging, counter_cycles])
    
                else:
                    counter_cycles+=1
          
    return averages

""""""""""""""""""""""""""""""""""""""""""""

def LFit(x,y,start,rmin):
    import numpy as np
    
    tminuses = []
    for i in range(len(x)):
        time = x[i]
        tminus = abs(time - start)
        tminuses.append(tminus)
    for i in range(len(tminuses)):
        if tminuses[i]==min(tminuses):
            start_index = i
            start = x[i]
    ni = len(x)
    x = [x[i] for i in range(start_index,ni)]
    y = [y[i] for i in range(start_index,ni)]
    
    deleted = []
    counter = 0
       
    while counter < ni + 1:
        nf = len(y)
        counter +=1 
                    
        y_bar = np.mean(y)
        x_bar = np.mean(x)

        denom = 0
        num = 0
        y_denom = 0
        
        for i in range(nf):
            num += (x[i] - x_bar)*(y[i] - y_bar)
            denom += (x[i]-x_bar)**2
            y_denom += (y[i]-y_bar)**2
    
        B = num/denom
        alpha = y_bar - B*x_bar
        Y = [alpha + B*x[i] for i in range(nf)]
        e = [Y[i]-y[i] for i in range(nf)]
        abs_e = [np.abs(e[i]) for i in range(nf)]
        
        r = num/np.sqrt(denom*y_denom)
        
        if np.abs(r) < rmin:
            j = abs_e.index(max(abs_e))
            deleted.append((j,y[j],x[j],e[j]))
            del(y[j])
            del(x[j])
            del(Y[j])
            del(e[j])
        
        # else:
        #     break
   
    rejrate = 100*(1-(nf/ni))
    numdelete = ni - nf
    
    return x, y, Y, e, r, alpha, B, rejrate, numdelete

""""""""""""""""""""""""""""""""""""""""""""

def tf_linearfit(averages, startpoints, r_mins, mode):
    from analysis_module import LFit
    
    ys = []
    xs = []
    Ys = []
    es = []
    rs = []
    tfs = []
    alphas = []
    Bs = []
    for k in range(len(averages)):
        
        device = averages[k]        
        y = []
        x = []
        for l in range(len(device)):
            row = device[l]
            dev = int(float(row[2]))
            x.append(float(row[0]))
            if mode == "APC":
                y.append(float(row[4]))
            if mode =="ACC":
                y.append(float(row[6]))
        
        
        start = startpoints[dev]
        r_min = r_mins[dev]
        
        x2, y2, Y, e, r, alpha, B, rejrate, numdelete = LFit(x,y,start,r_min)
        
        # Y = [Y[i]/y2[0] for i in range(len(y2))]
        # e = [e[i]/y2[0] for i in range(len(y2))]
        # alpha = alpha/y2[0]
        # B = B/y2[0]
        # y2 = [y2[i]/y2[0] for i in range(len(y2))]
        
        if r>=0:
            eol = 1.5
        else:
            eol = 0.5
        
        tf = (eol*y2[0] - alpha)/B
        
        xs.append(x2)
        ys.append(y2)
        Ys.append(Y)
        es.append(e)
        rs.append(r)
        tfs.append(tf)
        alphas.append(alpha)
        Bs.append(B)
    
    return xs, ys, Ys, es, rs, tfs, alphas, Bs

""""""""""""""""""""""""""""""""""""""""""""

def mttf_linearfit(tfs_sorted, r_min):

    from analysis_module import LFit

    fails = [i+1 for i in range(len(tfs_sorted))]
    
    failure_freq = [100*i/len(fails) for i in fails]
    start = 0
    x, y, Y, e, r, alpha, B, rejrate, numdelete = LFit(tfs_sorted, failure_freq, start, r_min)
    
    mttf = (50 - alpha)/B
    # import numpy as np
    # x = np.log(x)
    # y = np.log(y)
    # Y = np.log(Y)
    
    return x, y, Y, e, r, alpha, B, mttf
    
""""""""""""""""""""""""""""""""""""""""""""