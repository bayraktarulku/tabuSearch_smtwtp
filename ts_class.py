import pandas as pd
import random as rd
from itertools import combinations
# from pprint import pprint

class TabuSearch():
    def __init__(self, Path, seed, tabu_tenure, Penalization_weight):
        self.Path = Path
        self.seed = seed
        self.tabu_tenure = tabu_tenure
        self.Penalization_weight = Penalization_weight
        self.instance_dict = self.input_data()
        self.Initial_solution = self.get_InitialSolution()
        self.tabu_str, self.Best_solution, self.Best_objvalue = self.TSearch()


    def input_data(self):
        # tek makine toplam ağırlıklı geç kalma problemini (SMTWTP)
        # örneklerin excel dosyasının yolu alınır.
        # Değer olarak;
        # key, weight, processing time (hours) and due date (hours)

        return pd.read_excel(self.Path, names=['Job', 'weight', 'processing_time', 'due_date'],
                                 index_col=0).to_dict('index')


    def get_tabuestructure(self):
        # Bir dizi planlanmış işi alır (input_data -> self.instance_dict)
        # Anahtarlar ve [tabu_time, MoveValue] olarak tabu özniteliklerinin
        # (değiştirilen iş çiftleri) bir dizisini döndürür

        dict = {}
        for swap in combinations(self.instance_dict.keys(), 2):
            dict[swap] = {'tabu_time': 0, 'MoveValue': 0,
                          'freq': 0, 'Penalized_MV': 0}
        return dict


    def get_InitialSolution(self, show=False):
        n_jobs = len(self.instance_dict) # Yapılacak iş sayısı
        # Rastgele bir iş programı oluştur
        initial_solution = list(range(1, n_jobs+1))
        rd.seed(self.seed)
        rd.shuffle(initial_solution)
        if show == True:
            # TA algoritması, bir başlangıç çözümü
            # Rastgele ilk çözüm
            print('initial Random Solution: {}'.format(initial_solution))
        return initial_solution


    def obj_fun(self, solution, show = False):
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


    def SwapMove(self, solution, i ,j):
        # Bir dizi planlanmış işi alır (input_data -> self.instance_dict)
        # rastgele değiştirilen öğelerle yeni bir komşu çözümü döndürür

        solution = solution.copy()
        # çözümdeki iş dizisi
        i_index = solution.index(i)
        j_index = solution.index(j)
        # Değiştir
        solution[i_index], solution[j_index] = solution[j_index], solution[i_index]
        return solution


    def TSearch(self):
        # Uzun süreli belleğe sahip uygulama Tabu arama algoritması ve Tabu niteliği olarak pair_swap.

        # parametreler
        # ilk çözüm
        # ilk çözümün objvalue
        tenure = self.tabu_tenure
        tabu_structure = self.get_tabuestructure()  # Bir tabu yapısu oluşturulur.
        print('tabu_structure', tabu_structure)
        best_solution = self.Initial_solution # TA algoritması, bir başlangıç çözümü belirlenir
        best_objvalue = self.obj_fun(best_solution) # Başlangıç çözümünün amaç fonk. değeri hesaplanır
        current_solution = self.Initial_solution # Belirlenen başlangıç çözümü, mevcut çözüm olarak atanır
        current_objvalue = self.obj_fun(current_solution) # Başlangıç çözümünün amaç fonk. değeri mevcut amaç fonk olarak atanır

        print('#' * 30, 'Short-term memory TS with Tabu Tenure: {} \nInitial Solution: {}, Initial Objvalue: {}'.format(
            tenure, current_solution, current_objvalue), '#' * 30, sep='\n\n')
        iter = 1
        Terminate = 0
        # for i in range(50):
        while Terminate < 100:
            print(
                '\n\n### iter {}###  Current_Objvalue: {}, Best_Objvalue: {}'\
                .format(iter, current_objvalue, best_objvalue))

            # Mevcut çözümün tüm mahallesi aranır
            for move in tabu_structure:
                candidate_solution = self.SwapMove(current_solution, move[0], move[1])
                candidate_objvalue = self.obj_fun(candidate_solution)
                tabu_structure[move]['MoveValue'] = candidate_objvalue

                # Obj Değerine frekans ekleyerek cezalandırılmış obj Değeri (minimizasyon) atanır:
                tabu_structure[move]['Penalized_MV'] = candidate_objvalue + (tabu_structure[move]['freq'] *
                                                                             self.Penalization_weight)

            # eğer kabul edilebilir hareket ise;
            while True:
                # mahalledeki en düşük Obj Değeri(küçültme) olan hareket seçlir
                best_move = min(tabu_structure, key =lambda x: tabu_structure[x]['Penalized_MV'])
                MoveValue = tabu_structure[best_move]['MoveValue']
                tabu_time = tabu_structure[best_move]['tabu_time']
                print('tabu_time', tabu_time)
                # Penalized_MV = tabu_structure[best_move]['Penalized_MV']
                # Eğer tabu değil ise;
                if tabu_time < iter:
                    # make the move
                    current_solution = self.SwapMove(current_solution, best_move[0], best_move[1])
                    current_objvalue = self.obj_fun(current_solution)
                    # iyileştirme Hareketi
                    if MoveValue < best_objvalue:
                        best_solution = current_solution
                        best_objvalue = current_objvalue
                        print(
                            'best_move: {}, Objvalue: {} => Best Improving => Admissible'\
                            .format(best_move, current_objvalue))
                        Terminate = 0
                    else:
                        print(
                            '##Termination: {}## best_move: {}, Objvalue: {} => Least non-improving => '
                            'Admissible'.format(Terminate, best_move, current_objvalue))
                        Terminate += 1
                    # update tabu_time for the move and freq count
                    tabu_structure[best_move]['tabu_time'] = iter + tenure
                    tabu_structure[best_move]['freq'] += 1
                    iter += 1
                    break
                # Eğer tabu ise;
                else:
                    # Aspiration
                    if MoveValue < best_objvalue:
                        # make the move
                        current_solution = self.SwapMove(current_solution, best_move[0], best_move[1])
                        current_objvalue = self.obj_fun(current_solution)
                        best_solution = current_solution
                        best_objvalue = current_objvalue
                        print('best_move: {}, Objvalue: {} => Aspiration => Acceptable'.\
                            format(best_move, current_objvalue))
                        tabu_structure[best_move]['freq'] += 1
                        Terminate = 0
                        iter += 1
                        break
                    else:
                        tabu_structure[best_move]['Penalized_MV'] = float('inf')
                        print('best_move: {}, Objvalue: {} => Tabu => Unacceptable'.format(best_move,
                                                                                              current_objvalue))
                        continue
        print(
            '#'*50 ,
            'Performed iterations: {}'.format(iter), 'Best found Solution: {} , Objvalue: {}'.\
             format(best_solution,best_objvalue), sep='\n')
        return tabu_structure, best_solution, best_objvalue


test = TabuSearch(Path='dataset/instance_10.xlsx', seed=2012, tabu_tenure=3, Penalization_weight=0.6)
# test = TabuSearch(Path='Data_instances/Instance_50.xlsx', seed=2012, tabu_tenure=6, Penalization_weight=0.8)
