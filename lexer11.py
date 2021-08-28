# -*- coding: utf-8 -*-
#Import Lexer from sly(Sly Lex Yacc)
from sly import Lexer
from sly import Parser



# ****NOT**** 
    # Lexer yazdigimiz ifadedeki butun tokenlerimizi donduruyor.
    # "@_" şeklinde verlilen satırlar dilin gramerini gostermektedir
    # Parser ise syntaxi kontrol eder. 
    # Mesela if uzerinden ornek vererek aciklamaya calisalim;
    # Lexer kisminda EQEQ'ya baktığımızda "==" oldugunu goruyoruz.(53.satir)
    # Condition icin @_('expr EQEQ expr') bu gramer verilmis yani 
    # Herhangi 2 expression'ın arasina "==" getirilmelidir. Ornegin 1==2 gibi
    # Simdi if icin olan gramerimizi inceleyelim.
    # @_('IF condition THEN statement ELSE statement')
    # IF'den sonra gelen kisim daha yeni anlattığımız condition kısmından olusması gerekiyor 
    # ve daha sonra THEN diyerek yapmak istediğimiz statement'i belirlemeliyiz. 
    # Bu statement bir deger atama islemi olabilir(asagida def statement kisminda @_('var_assign').
    # seklinde verilmis burdan gorebiliriz.
    # Daha sonrada ELSE diyerek bir statement daha ekliyoruz THEN'den sonra yazdigimiz statement1 
    # ELSE'den sonra yazdigimiz statement2 olmus oluyor
    # ORNEK/ 
    # a=10
    # b=20
    # IF a==10 THEN b="Hello World" ELSE b=5
    # Buraya kadar aslinda sadece lexerle tokenleri ayirdik ve parser ile syntax kontrolu yaptik
    # Basic Execute kisminda ise burada yapilan işlemleri compilerdan nasil cikicagini ayarliyoruz.
    # ORNEK / 
    # Lexer ve Parser'dan sonraki ciktimiz: 
    # ('if_stmt', ('condition_eqeq', ('var', 'a'), ('num', 10)), ('branch', ('var_assign', 'b', '"Hello World"'), ('var_assign', 'b', ('num', 5))))
    # # Basic execute'a gidicek seyler;
    # if_stmt, condition_eqeq, var, var_assign ve num degerleriymis
    # Bu degerlerimizi BasicExecute kismandan aldigimiz returnler ile elde ettigimiz cikti
    # "Hello World" olmus oluyor. 
    
#Basic Lexer 
class BasicLexer(Lexer):
    # Bu tokenler bizim dilimizin anlayabilecegi tokenleri ifade eder. 
    tokens = { NAME, NUMBER, STRING, IF, ELSE, THEN, FOR, FUN, TO, ARROW, EQEQ }
    ignore = '\t ' # Bosluklari ve tab'leri engeller
    # Bunlar +,-,= vb gibi olan 1 karakterli tokenler
    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';'}


    #Tokenleri regular expression olarak tanimliyoruz
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    FOR = r'FOR'
    FUN = r'FUN'
    TO = r'TO'
    ARROW = r'->'
    EQEQ = r'=='
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*' # Degisken ismi bir harf veya _ ile baslayabili
                                    # * ise bu karakterlerden sonra istedigin kadar harf ekleyebilecegini soyler
    STRING = r'\".*?\"'     # Bize cift tirnak arasinda olan herhangi bir seyin string ifadesi oldugunu gosterir

    #Sayi Tokeni
    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value) #Python'da integer degerine cevir
        return t   # ve sadece cevirdigin degeri dondur

    #Yorum tokeni
    @_(r'//.*')
    def COMMENT(self, t):
        pass  # Bir sey dondurme

    #Yeni Satir Tokeni(Sadece errorleri yeni satırda göstermek icin kullanildi)
    @_(r'\n+')
    def newline(self, t):
        # Yeni bir satir gorursek satir sayisi degiskenini artiracagiz(Bu degisken = lineo)
        self.lineno = t.value.count('\n') 


#Basic Parser
class BasicParser(Parser):
    # Tokenleri lexerdan parsera gecir
    tokens = BasicLexer.tokens
    # Islemlerde oncelik verilcek durumlar
    # Carpma ve bolme islemlerini toplama ve cikarmadan once yapmasini soyluyoruz
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.env = { }
    @_('')
    def statement(self, p): # Statement bos donebilir
    # Bos donerse hicbir sey yapma
        pass
    # For'dan sonra bir degisken ile baslamali ve bu Expression kismima gidicek
    # ORNEK/ FOR i=0 TO 10 THEN i
    @_('FOR var_assign TO expr THEN statement')
    def statement(self, p):
                # for loop setup, first_child, variable,   iteration, second_child
        return ('for_loop', ('for_loop_setup', p.var_assign, p.expr), p.statement)
    
    # IF'den sonra bir condition gelir ve THEN diyiop bir statement ve ELSE diyip bir statement daha yazilir
    @_('IF condition THEN statement ELSE statement')
    def statement(self, p):
        #				root	left branch				right branch
        return ('if_stmt', p.condition, ('branch', p.statement0, p.statement1))
    
    # Fonksiyon yapma
    # FUN'dan sonra parantez acilip kapatilir daha sonra bir ok yapip statement yazilir 
    # ORNEK/ FUN Hello () -> statement
    @_('FUN NAME "(" ")" ARROW statement')
    def statement(self, p):
        return ('fun_def', p.NAME, p.statement)

    @_('NAME "(" ")"')
    def statement(self, p):
        return ('fun_call', p.NAME)

    @_('expr EQEQ expr') # Esit ise
    def condition(self, p):
        return ('condition_eqeq', p.expr0, p.expr1)

    @_('var_assign') # Degisken atamasi
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr') # Degisken atamasi bir expression olabilir
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME "=" STRING') # Degisken atamasi string olabilir
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)
    
    @_('expr') 
    def statement(self, p):
        return (p.expr)
    
    # iki expression'in arasinda + varsa basic lexer'da add kismini calistir
    # ORNEK 5+7
    # Lexer ve parser ciktisi;
    # ('add', ('num', 5), ('num', 7))
    # Basic lexer calisirken
    # Gordugumuz uzere Node[0]='add' da Node[1]= ('num', 5) ve Node[2]= ('num', 7)
    # node[0]== 'add' oldugu icin basic lexer'de add fonksiyonu calisir ve 
    # Node[1]+Node[2] degerini dondurur
    # Yani 5+7 'den 12 ciktisini elde ederiz
    # Bu durum diger islemler icin de aynidir
    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('NAME') # expression sadece bir degisken olabilir
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER') # expression sadece bir sayi olabilir
    def expr(self, p):
        return ('num', p.NUMBER)


#Basic Interpreter
class BasicExecute:
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'str':
            return node[1]

        if node[0] == 'if_stmt':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[2][1])
            return self.walkTree(node[2][2])

        if node[0] == 'condition_eqeq':
            return self.walkTree(node[1]) == self.walkTree(node[2])

        if node[0] == 'fun_def':
            self.env[node[1]] = node[2]

        if node[0] == 'fun_call':
            try:
                return self.walkTree(self.env[node[1]])
            except LookupError:
                print("Undefined function '%s'" % node[1])
                return 0

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0

        if node[0] == 'for_loop':
            if node[1][0] == 'for_loop_setup':
                loop_setup = self.walkTree(node[1])

                loop_count = self.env[loop_setup[0]]
                loop_limit = loop_setup[1]

                for i in range(loop_count+1, loop_limit+1):
                    res = self.walkTree(node[2])
                    if res is not None:
                        print(res)
                    self.env[loop_setup[0]] = i
                del self.env[loop_setup[0]]

        if node[0] == 'for_loop_setup':
            return (self.walkTree(node[1]), self.walkTree(node[2]))


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    
    env = {}
    while True:
        try:
            # girilen degeri text'e ata
            text = input('Cihan-Compiler > ')
        except EOFError:
            break
        if text:
            # texti lexer'de tokinlerine ayır ve parserda kontrol ettir
            tree = parser.parse(lexer.tokenize(text))
            # Gelen degerleri BasicExecute'a gonderip elde etmek istedigimiz ciktilari al
            BasicExecute(tree, env)
