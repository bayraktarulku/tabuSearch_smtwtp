import pandas as pd
import random as rd
import math

class SA():
    def __init__(self, Path, initial_temp, epoch, cooling_rate):
        self.Path = Path
        self.instance_dict = self.input_data()
        self.initial_temp = initial_temp
        self.epoch = epoch
        self.cooling_rate = cooling_rate
        self.best_li = []
        self.current_li = []
        self.itr_li = []
        self.Best_solution, self.Best_objvalue = self.SimuAnn()

    def input_data(self):
        # tek makine toplam ağırlıklı geç kalma problemini (SMTWTP)
        # örneklerin excel dosyasının yolu alınır.
        # Değer olarak;
        # key, weight, processing time (hours) and due date (hours)

        return pd.read_excel(self.Path, names=['Job', 'weight', 'processing_time', 'due_date'],
                                 index_col=0).to_dict('index')


    def get_InitialSolution(self, show=False):
        n_jobs = len(self.instance_dict) # Yapılacak iş sayısı
        # Rastgele bir iş programı oluştur
        initial_solution = list(range(1, n_jobs+1))
        rd.seed(self.seed)
        rd.shuffle(initial_solution)
        if show == True:
            # Rastgele ilk çözüm
            print('initial Random Solution: {}'.format(initial_solution))
        return initial_solution


    def Objfun(self, solution, show = False):
        # Bir dizi planlanmış işi alır (input_data -> self.instance_dict)
        # Çözümün amaç fonksiyon değerini döndür

        dict = self.instance_dict
        t = 0   # başlangıç zamanı
        objfun_value = 0
        for job in solution:
            C_i = t + dict[job]['processing_time']  # Tamamlama zamanı
            d_i = dict[job]['due_date']   # işin bitiş zamanı
            T_i = max(0, C_i - d_i)    # işin gecikme payı/zamanı
            W_i = dict[job]['weight']  # işin ağırlığı

            objfun_value +=  W_i * T_i
            t = C_i
        if show == True:
            # Çözüm çizelgesi için Amaç işlevi değeri:
            print(
                '\n', '#'*8,
                'The Objective function value for {} solution schedule is: {}'\
                .format(solution ,objfun_value), '#'*8)
        return objfun_value


    def SwapMove(self, li, show = False):
        # Bir dizi planlanmış işi alır (input_data -> self.instance_dict)
        # rastgele değiştirilen öğelerle yeni bir komşu çözümü döndürür

        li = li.copy()
        # çözümdeki iş dizisi
        pos1 = rd.randint(0, len(li) - 1) # rastgele iki iş seçme
        pos2 = rd.randint(0, len(li) - 1)
        if pos1 != pos2:
            li[pos1], li[pos2] = li[pos2], li[pos1]

        while pos1 == pos2:
            pos1 = rd.randint(0, len(li) - 1)  # rastgele iki iş seçme
            pos2 = rd.randint(0, len(li) - 1)
            if pos1 != pos2:
                li[pos1], li[pos2] = li[pos2], li[pos1]
                break
        if show == True:
            # mevcut çözüm sırası güncellenir
            print(
                '{} and {} are swapped, the current solution sequance is: {}'\
                 .format(li[pos1], li[pos2], li))
        return li


    def SimuAnn(self):
        # Uygulama Rastgele takas hareketiyle Simüle Edilmiştir: Tavlama algoritması (neighborhood operator)
        # Giriş: Başlangıç sıcaklığı(T_0), Epoch uzunluğu(epo), Durdurma Sıcaklığı(T_f)
        # Çıktı: Bulunan en iyi çözüm ve ilgili çözümün Objfun Değeri

        # SA Parameters:
        T_0 = self.initial_temp
        maxepo = self.epoch
        cooling_fun = lambda x: x * self.cooling_rate
        T_f = 0.001

        best_solution = []
        best_objvalue = float('inf')
        current_solution = self.get_InitialSolution()  # ilk yinelemede rastgele ilk çözümü atanır
        current_objvalue = self.Objfun(current_solution)

        T = T_0  # Mevcut sıcaklık
        current_iter = 1
        # Planlanacak işlerin sayısı
        print("\n\nNumber of jobs to be scheduled: {}".format(len(current_solution)))

        print("\nInitial Solution: {}  Initial Objfun value: {}\n\n".format(current_solution, current_objvalue))

        while T >= T_f :
            self.itr_li.append(current_iter)
            self.current_li.append(current_objvalue)
            self.best_li.append(best_objvalue)
            epoch = int(0)
            while epoch < maxepo:

                print("### iter: {}/ epoch: {} ### current_temp: {}, current_objfun: {}, best_Objfun: {}".format(current_iter, epoch, T,current_objvalue,best_objvalue))

                # rastgele takas hareketiyle komşu oluştur
                candidate_solution = self.SwapMove(current_solution)
                candidate_objvalue = self.Objfun(candidate_solution)

                # Bulunan iyileştirme çözümü
                if candidate_objvalue <= current_objvalue:
                    current_solution, current_objvalue = candidate_solution ,candidate_objvalue
                   # En iyi çözüm güncellenir
                    if current_objvalue < best_objvalue:
                        best_solution, best_objvalue = current_solution, current_objvalue

                    print(" "*5, "Candidate Solution: Objfun= {},  Sequence= {}   =>  Improved Solution  => Accepted\n".format(candidate_objvalue, candidate_solution))

                #non_imporving solution
                else:
                    degradation = candidate_objvalue - current_objvalue
                    metropolis = math.exp(-(degradation/T))
                    x = rd.random()
                    # Metropolis kriterine göre iyileştirme içermeyen çözümü kabul eder
                    if x <= metropolis:
                        current_solution, current_objvalue = candidate_solution ,candidate_objvalue
                        print(" "*5, "Candidate Solution: Objfun= {},  Sequence= {}   =>  Non_improved Solution => Metropolis => Accepted\n".format(candidate_objvalue, candidate_solution))
                    else:
                        print(" "*5, "Candidate Solution: Objfun= {},  Sequence= {}   =>  Non_improved Solution => Metropolis  => Not Accepted\n".format(candidate_objvalue, candidate_solution))
                # parametre güncellenir
                epoch += 1
            # sıcaklık & iterasyon değeri güncellenir
            T = cooling_fun(T)
            current_iter += 1
        print(
            '#'*30,
            '\nNumber of iteration performed: {}\nFinal Temperature: {}\nBest Objvalue: {}\nBest Solution: {}'\
            .format(current_iter, T, best_objvalue, best_solution))
        return best_solution, best_objvalue


    def Save_file(self, file_name):
        df = pd.DataFrame(list(zip(self.itr_li, self.current_li, self.best_li)), columns = ['itr', 'current', 'best'])
        df.to_excel(file_name)