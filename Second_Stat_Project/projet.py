# Mohamed Elyes Bourenane
# David Kitoko

from utils import *
import pandas as pd
import numpy as np
import matplotlib
import scipy.stats as stats
import matplotlib.pyplot as plt

def getPrior(data):
    """
        Calculer la probabilité a priori de la classe $1$ ainsi que l'intervalle de confiance à 95% pour l'estimation de cette probabilité.
        Parametes
        ---------
            data : pandas.dataframe
                le `pandas.dataframe` contenant les données
        
        Returns
        ---------
            Dict[str,float]
                un dictionnaire incluant l'estimation, min5pourcent, max5pourcent
    """

    moyenne = data["target"].sum() / len(data["target"])
    ecart_type = (moyenne * (1 - moyenne) / len(data["target"]))**0.5



    return {"estimation": moyenne, "min5pourcent": moyenne - 1.96 * ecart_type, "max5pourcent": moyenne + 1.96 * ecart_type}

class APrioriClassifier(AbstractClassifier):
    def __init__(self):
        self.prop_apriori = 0

    def estimClass(self, attrs):
        """
        à partir d'un dictionanire d'attributs, estime la classe 0 ou 1

        Parameters
        ---------
        attrs: Dict[str,val] 
            Le dictionnaire nom-valeur des attributs

        Returns
        -------
        la classe 0 ou 1 estimée
        """
        return 1 if self.prop_apriori >= 0.5 else 0
    
    def statsOnDF(self, df):
        """
        à partir d'un pandas.dataframe, calcule les taux d'erreurs de classification et rend un dictionnaire.

        Parameters
        ----------
        df:  pandas.DataFram
            le dataframe à tester
        
        Returns
        -------
        Dict[str,float]
            un dictionnaire incluant les VP,FP,VN,FN,précision et rappel
        """

        VP = 0
        VN = 0
        FP = 0
        FN = 0

        self.prop_apriori = getPrior(df)["estimation"]

        for i in range(len(df)):
            dic = getNthDict(df, i)
            classe_predite = self.estimClass(dic)

            if dic["target"] == 1:
                if classe_predite == 1:
                    VP += 1
                else:
                    FN += 1
            else:
                if classe_predite == 1:
                    FP += 1
                else:
                    VN += 1
        
        precision = VP / (VP + FP) if (VP + FP) > 0 else 0
        rappel = VP / (VP + FN) if (VP + FN) > 0 else 0

        return {'VP': VP, 'VN': VN, 'FP': FP, 'FN': FN, 'Précision': precision, 'Rappel': rappel}
    
def P2D_l(df, attr):
    """
        calcule dans le dataframe la probabilité  P(attr|target)

        Parameters
        ----------
        df:  pandas.DataFram
            le dataframe à tester
        attr: string
            le nom de la colonne
        
        Returns
        -------
        Dict[int,float]
            un dictionnaire de la loi de probabilité P(attr|target)
    """
    probabilites = {}
    unique_targets = df['target'].unique()

    for target_value in unique_targets:
        filtered_df = df[df["target"] == target_value]

        nb_attr = filtered_df[attr].value_counts().to_dict()

        nb_total = len(filtered_df)

        probabilites[target_value] = {attr_value: count / nb_total for attr_value, count in nb_attr.items()}

    return probabilites

def P2D_p(df,attr):
    """
        calcule dans le dataframe la probabilité  P(target|attr)

        Parameters
        ----------
        df:  pandas.DataFram
            le dataframe à tester
        attr: string
            le nom de la colonne
        
        Returns
        -------
        Dict[int,float]
            un dictionnaire de la loi de probabilité P(target|attr)
    """

    probabilites = {}
    unique_attr = df[attr].unique()

    for attr_value in unique_attr:
        filtered_df = df[df[attr] == attr_value]

        nb_target = filtered_df["target"].value_counts().to_dict()

        nb_total = len(filtered_df)

        probabilites[attr_value] = {target_value : count / nb_total for target_value, count in nb_target.items()}

    return probabilites

class ML2DClassifier(APrioriClassifier):
    """ Initialise un classifieur maximum de vraissemblance pour estimer la classe d'un individu en utilisant les lois de probabilité 
    conditionnelles P(attr|target) 
    """
    
    def __init__(self, df, attr):
        super().__init__
        self.attr = attr
        self.P2D_l = P2D_l(df, attr)

    def estimClass(self, attrs):
        """
        A partir d'un dictionanire d'attributs en utilisant le maximum de vraissemblance, estime la classe 0 ou 1

        Parameters
        ---------
        attrs: Dict[str,val] 
            Le dictionnaire nom-valeur des attributs

        Returns
        -------
        la classe 0 ou 1 estimée
        """
        if self.attr in attrs:
            attr_value = attrs[self.attr]
            max_likehood = max(self.P2D_l.keys(), key=lambda target: self.P2D_l[target].get(attr_value, 0))
            return max_likehood
        return 0


class MAP2DClassifier(APrioriClassifier):
    """ Classifieur maximum à posteriori pour estimer la classe d'un individu 
    """
    
    
    def __init__(self, df, attr):
        super().__init__()
        self.attr = attr
        self.P2Dp = P2D_p(df,attr)

    

    def estimClass(self, attributs):
        """
        Estime la classe d'un individu en utilisant les attributs fournis.

        Parameters
        ---------
        attrs: Dict[str,val] 
            Le dictionnaire nom-valeur des attributs

        Returns
        -------
        la classe 0 ou 1 estimée
        """
        
        if self.attr in attributs:
            attr_value = attributs[self.attr]            
            max_posterior_class = max(self.P2Dp[attr_value].keys(), key=lambda target: self.P2Dp[attr_value].get(target, 0))
            return max_posterior_class

        return 0
    
#####
# Question 2.4 : comparaison
#####

# 1. **APrioriClassifier** :
#    - Précision en validation : 0.69
#    - Rappel en validation : 1.0

#    Ce classifieur a une précision modérée en validation, ce qui signifie qu'il peut donner un grand nombre de faux positifs (FP) par rapport aux vrais positifs (VP). Cependant, il a un rappel élevé, ce qui signifie qu'il capture correctement tous les vrais positifs, mais au détriment d'un nombre plus élevé de faux positifs.

# 2. **ML2DClassifier (Maximum Likelihood)** :
#    - Précision en validation : 0.8898
#    - Rappel en validation : 0.8188

#    Le ML2DClassifier montre une amélioration significative de la précision par rapport à l'APrioriClassifier en validation, réduisant ainsi le nombre de faux positifs. Cependant, le rappel a légèrement diminué, ce qui signifie qu'il pourrait manquer certains vrais positifs.

# 3. **MAP2DClassifier (Maximum A Posteriori)** :
#    - Précision en validation : 0.8571
#    - Rappel en validation : 0.8261

#    Le MAP2DClassifier se situe entre l'APrioriClassifier et le ML2DClassifier en termes de précision. Il offre un bon équilibre entre la réduction des faux positifs et le maintien d'un rappel décent.

# Si on souhaite minimiser les faux positifs, le ML2DClassifier peut être préférable en raison de sa meilleure précision. Si on souhaite maintenir un bon équilibre entre la précision et le rappel, le MAP2DClassifier pourrait être un bon choix.
#####

def size_format(size):
    """
    Etant donné une taille en octets, retourne une valeur de taille donnée en une chaîne avec des unités appropriées (To, Go, Mo, Ko, o)    

    Parameters
     ---------
      size : int 
          La taille en octets à formater.
       

    Returns
    -------
       Une valeur de taille donnée en une chaîne avec des unités appropriées (To, Go, Mo, Ko, o) 
    """
    output = ""
    units = ["To", "Go", "Mo", "Ko", "o"]
    while size != 0:
        output = "{}{} ".format(size % 1024, units.pop()) + output
        size //= 1024
    return output

def nbParams(df,attrs: list=None):
    """
    Etant donné un dataframe et une liste des attributs, retourne Le nombre d'octets nécessaires pour la construction d'un classifieur       

    Parameters
     ---------
      df : pandas.DataFram
        le dataframe à tester
        
      attrs: list
        la liste d'attributs à prendre en compte

    Returns
    -------
       Le nombre d'octets nécessaires pour la construction d'un classifieur  
    """
    if attrs is None:
        attrs = df.keys()
    size = 8
    for attr in attrs:
        size *= len(np.unique(df[attr]))
        
    output = "{} variable(s) : {} octets".format(len(attrs), size)
    if size < 1024:
        print(output)
    else:
        print(output + " = " + size_format(size))
        
    return size

def nbParamsIndep(df):
    """
    Etant donné un dataframe, retourne Le nombre d'octets nécessaires pour la construction d'un classifieur en supposant l'indépendance des  
    variables       

    Parameters
     ---------
      df : pandas.DataFram
        le dataframe à tester


    Returns
    -------
       Le nombre d'octets nécessaires pour la construction d'un classifieur en supposant l'indépendance des variables       
    """
    attrs = df.keys()
    size = 0
    for attr in attrs:
        size += len(np.unique(df[attr]))
       
    output = "{} variable(s) : {} octets".format(len(attrs), 8*size)
  
    if size < 1024:
        print(output)
    else:
        print(output + " = " + size_format(size))
  
    return 8 * size


####
# Question 3.3 :  indépendance partielle

# Question 3.3.a : preuve $$P(A,B,C)=P(A)*P(B|A)*P(C|B)$$
####

#L'indépendance conditionnelle entre les variables aléatoires A, B et C sachant B signifie que la probabilité de A ne dépend pas de C #lorsqu'on connaît la valeur de B. Donc : $$P(A∣ B,C) = P(A∣ B)$$
# décomposons la loi jointe P(A,B,C) en utilisant cette indépendance conditionnelle : 
# $$P(A,B,C) = P(A∣ B,C)∗ P(B,C)$$ <-> $$P(A,B,C) = P(A∣ B) ∗ P(B,C)$$ (loi d'indépendance conditionnelle)
#                                 <-> $$P(A,B,C) = P(A∣ B) * P(B∣ C)∗ P(C)$$ (loi de probabilité conditionnelle)
#                                 <-> $$P(A,B,C) = (P(B∣ A) * P(A)/p(B)) * P(B∣ C)* P(C)$$ (Théorème de Bayes)
#                                 <-> $$P(A,B,C) = P(B∣ A) * P(A) * P(C∣ B)$$ (simplification)
#
#Nous avons montré que l'indépendance conditionnelle entre A, B et C sachant B se traduit par une expression concise de la loi jointe #$$P(A,B,C) = P(A) * P(B∣ A) * P(C∣ B)$$

# Question 3.3.b : complexité en indépendance partielle

# Sans l'utilisation de l'indépendance conditionnelle :
# Chaque variable A, B, et C a 5 valeurs possibles, ce qui signifie qu'il y a 5×5×5 =125 combinaisons possibles
#Chaque probabilité peut être représentée par un nombre flottant sur 8 octets, donc La taille mémoire nécessaire sans l'utilisation de #l'indépendance conditionnelle serait donc de 125×8=1000  octets.

#Avec l'utilisation de l'indépendance conditionnelle :
#P(A), P(B∣ A), et P(C∣ B) nécessitent 5 nombres flottants chacun, ce qui donne un total de 5×3=15 nombres flottants possibles
#Chaque probabilité peut être représentée par un nombre flottant sur 8 octets, donc La taille mémoire nécessaire sans l'utilisation de #l'indépendance conditionnelle serait donc de 15×8=120  octets.

#Conclusion : 
# Cette étude met en lumière l'importance de l'indépendance conditionnelle dans la modélisation des distributions de probabilités. En #supposant certaines formes d'indépendance partielle, nous pouvons considérablement réduire la quantité de mémoire nécessaire pour #représenter ces distributions, tout en préservant des informations cruciales pour l'analyse statistique.


#Propositoin de code pour le 4.1 

#def draw_independent_graph():
    #arcs = 'A->B;A->C;A->D;A->E;B->C;B->D;B->E;C->D;C->E;D->E'
    #return drawGraphHorizontal(arcs)

# Dessin du graphe complètement indépendant
#img__independent = draw_independent_graph()
#img__independent.show()


#def draw_dependent_graph():
    #arcs = 'A->B;B->C;C->D;D->E'
    #return drawGraphHorizontal(arcs)

# Dessin du graphe sans aucune indépendance
#img_dependent = draw_dependent_graph()
#img_dependent.show()

#### Question 4.2 : 

#Dans un modèle Naïve Bayes, il est supposé que les attributs sont conditionnellement indépendants étant donné la cible (target). 
#Cela signifie que la vraisemblance,se décompose de la manière suivante : 
#P(att1,att2,att3,...∣target) = P(att1∣target) * P(att2∣target) * P(att3∣target) * ... * P(attn-1∣target)
#La distribution a posteriori,se décompose de la manière suivante : 
#P(att1,att2,att3,...∣target) ∝ P(att1∣target) * P(att2∣target) * P(att3∣target) * ... * P(attn-1∣target)
#avec attn-1 : dernier attribut de la liste d'attributs 

 
def drawNaiveBayes(df, attr):
    """
    A partir d'un dataframe et du nom de la colonne qui est la classe, dessine le graphe
    
    Parameters
     ---------
      df : pandas.DataFram
        le dataframe à tester
        
      attr : String
           le nom de la colonne qui est la classe

    Returns
    -------
       dessine le graphe 
    """
    graph = ""
    attrs = df.keys()
    for attr1 in attrs:
        if attr1 == attr: continue
        graph += attr + "->" + attr1 + ";"
    return drawGraph(graph)


def nbParamsNaiveBayes(df, attr,attrs: list=None):
    """
     Etant donné un dataframe, et en utilisant l'hypothèse du Naive Bayes , retourne la taille mémoire nécessaire pour représenter les 
     tables de probabilité d'un classifieur avec le modèle Naïve Bayes
     
      Parameters
     ---------
     
      df : pandas.DataFram
        le dataframe à tester
        
      attr : String
           le nom de la colonne qui est la classe
      
      attrs : list
             la liste des attributs 

    Returns
    -------
       retourne la taille mémoire nécessaire pour représenter les tables de probabilité d'un classifieur avec le modèle Naïve Bayes
     
    """
    if attrs is None:
        attrs = df.keys()
    size = 0
    for attr1 in attrs:
        if attr1 == attr: continue
        size += len(np.unique(df[attr1]))
        
    u = len(np.unique(df[attr]))
    size *= u
    size += u
    size = size * 8
    output = "{} variable(s) : {} octets".format(len(attrs), size)
    
    if size < 1024:
        print(output)
    else:
        print(output + " = " + size_format(size))
    return size

class MLNaiveBayesClassifier(APrioriClassifier):
    """
      Classifieur maximum de vraissemblance pour estimer la classe d'un individu en utilisant l'hypothèse du Naïve Bayes

    """

    def __init__(self, df):
        self.probas = {attr: P2D_l(df, attr) for attr in df.keys()}

    def estimProbas(self, attrs):
        """
        Etant donné une liste d'attributs, calcule la probabilité de vraissemblance
     
        Parameters
         ---------
      
          attrs : list
             la liste des attributs 

        Returns
        -------
         calcule la probabilité de vraissemblance
     
        """
        p_t0, p_t1 = 1, 1
        for attr in self.probas:
            if attr == 'target': continue
            p_attr = self.probas[attr]
            p_t0 *= p_attr[0][attrs[attr]] if attrs[attr] in p_attr[0] else 0
            p_t1 *= p_attr[1][attrs[attr]] if attrs[attr] in p_attr[1] else 0
        return {0: p_t0, 1: p_t1}

    def estimClass(self, attrs):
        p = self.estimProbas(attrs)
        return 1 if p[1] > p[0] else 0
    
class MAPNaiveBayesClassifier(APrioriClassifier):
    """
    Classifieur maximum à posteriori pour estimer la classe d'un individu en utilisant l'hypothèse du Naïve Bayes

    """

    def __init__(self, df):
        self.probas = {attr: P2D_l(df, attr) for attr in df.keys()}
        p = getPrior(df)['estimation']
        self.p1 = p 

    def estimProbas(self, attrs):
        """
        Etant donné une liste d'attributs, calcule la probabilité à posteriori
     
        Parameters
         ---------
      
          attrs : list
             la liste des attributs 

        Returns
        -------
         calcule la probabilité à posteriori
     
        """
        p_t0, p_t1 = 1-self.p1, self.p1
        for attr in self.probas:
            if attr == 'target': continue
            p_attr = self.probas[attr]
            p_t0 *= p_attr[0][attrs[attr]] if attrs[attr] in p_attr[0] else 0
            p_t1 *= p_attr[1][attrs[attr]] if attrs[attr] in p_attr[1] else 0
        pa = p_t0 + p_t1
        if pa != 0:
            p_t0 /= pa
            p_t1 /= pa
        return {0: p_t0, 1: p_t1}

    def estimClass(self, attrs):
        p = self.estimProbas(attrs)
        return 1 if p[1] > p[0] else 0
    

def isIndepFromTarget(df, attr, x):
    """
    Vérifie si l'attribut attr est indépendant de la classe cible target au seuil de x% en utilisant le test du chi-carré.

    Parameters
    ----------
    df : pandas.DataFrame
        Le dataframe contenant les données.

    attr : str
        Le nom de l'attribut que vous voulez tester.

    x : float
        Le seuil de confiance en pourcentage (0 < x < 100).

    Returns
    -------
    bool
        True si l'attribut est indépendant de la classe cible au seuil de x%, False sinon.
    """
    
    contingency_table = pd.crosstab(df[attr], df['target'],margins=True, margins_name="S")
    chi2 = 0
    for j in df['target'].unique():
        for i in df[attr].unique():
            res_Obsertion = contingency_table[j][i]
            res_attendues = contingency_table[j]['S'] * contingency_table['S'][i] / contingency_table['S']['S']
            chi2 += ((res_Obsertion - res_attendues)**2)/res_attendues
    return chi2 <= stats.chi2.ppf(1-x, len(df[attr].unique())-1)



class ReducedMLNaiveBayesClassifier(MLNaiveBayesClassifier):
    """
    classifieur à maximum de vraissemblance pour attributs non indépendants de target à partir d'un seuil
    """

    def __init__(self, df,x):
        self.keys_of_indep = self.get_keys(df, x)
        MLNaiveBayesClassifier.__init__(self,  df[self.keys_of_indep])
        

    def get_keys(self, df, x):
        """
        Récupère les noms des attributs non indépendants de la classe cible en utilisant un seuil donné.

        Parameters
        ----------
        df : pandas.DataFrame
            Le dataframe contenant les données.
            
        x : float
            Le seuil de confiance en pourcentage (0 < x < 100) pour déterminer l'indépendance des attributs par rapport à la classe cible.

        Returns
        -------
        list
            Une liste des noms des attributs non indépendants.
        """
        
        keys_of_indep = []
        for key in df.keys():
            if key == 'target' or not isIndepFromTarget(df, key, x):
                keys_of_indep.append(key)
        return keys_of_indep
    
    
    def draw(self):
        """
        Dessine un graphe de dépendance entre la classe cible et les attributs non indépendants.

        Returns
        -------
        None
              le graphe.
        """
        input_arg_str = ''
        keys = self.keys_of_indep.copy()
        for champ in keys:
            if champ != "target":
                input_arg_str += "{}->{};".format('target', champ)
      
        input_arg_str = input_arg_str[:-1]
        return drawGraph(input_arg_str)

class ReducedMAPNaiveBayesClassifier( MAPNaiveBayesClassifier):
    """ Classifieur à maximum a posteriori pour attributs non indépendants de la classe cible à partir d'un seuil. 
    """
    
    def __init__(self, df, x):
        self.keys_of_indep = self.get_keys(df, x)
        MAPNaiveBayesClassifier.__init__(self,  df[self.keys_of_indep])
    
    def get_keys(self, df, x):
        """
        Récupère les noms des attributs non indépendants de la classe cible en utilisant un seuil donné.

        Parameters
        ----------
        df : pandas.DataFrame
            Le dataframe contenant les données.
            
        x : float
            Le seuil de confiance en pourcentage (0 < x < 100) pour déterminer l'indépendance des attributs par rapport à la classe cible.

        Returns
        -------
        list
            Une liste des noms des attributs non indépendants.
        """
        keys_of_indep = []
        for key in df.keys():
            if key == 'target' or not isIndepFromTarget(df, key, x):
                keys_of_indep.append(key)
        return keys_of_indep
    
    def draw(self):
        """
        Dessine un graphe de dépendance entre la classe cible et les attributs non indépendants.

        Returns
        -------
        None
              le graphe.
        """
        input_arg_str = ""
        keys = self.keys_of_indep.copy()
        for champ in keys:
            if champ != "target":
                input_arg_str += "{}->{};".format('target', champ)
      
        input_arg_str = input_arg_str[:-1]
        return drawGraph(input_arg_str)

    
### Question 6.1
######
#Le point idéal dans un graphique de précision par rapport au rappel serait le point (1, 1), c'est-à-dire une précision maximale et un #rappel maximal. Cela signifierait que le classifieur est capable de faire des prédictions parfaites, sans erreurs. Cependant pour atteindre #ce point idéal cela est extrêmement difficile, voire impossible.
#Pour comparer différents classifieurs dans cette représentation graphiques, les classifieurs qui s'approchent le plus du coin supérieur #gauche (plus proche de (1,1) sur le graphique) sont considérés comme meilleurs, car ils ont à la fois une haute précision et un haut rappel. 

def mapClassifiers(dic, df):
    """
    Compare les performances de différents classifieurs en utilisant un DataFrame de données.

    Parameters
    ----------
    dic : dict
        Un dictionnaire où les clés sont des noms de classifieurs et les valeurs sont des instances de ces classifieurs.
        
    df : pandas.DataFrame
        Le DataFrame contenant les données à tester.

    Returns
    -------
    None
        Cette fonction n'a pas de valeur de retour, elle affiche un graphique pour comparer les performances des classifieurs.
    """
    
    for index, classifier in dic.items():
        stats = classifier.statsOnDF(df)
        x = stats['Précision']
        y = stats['Rappel']
        plt.scatter(x, y, marker='x', color="red")
        plt.text(x, y, index)
    plt.show()

