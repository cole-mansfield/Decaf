import antlr4 as ant
from DecafLexer import DecafLexer
from DecafParser import DecafParser
from DecafVisitor import DecafVisitor
from SymbolTable import HEAP, STACK, SymbolTable, VarSymbol, MethodSymbol

class DecafSemanticChecker(DecafVisitor):
        
    def __init__(self):
        super().__init__()
        self.st = SymbolTable()
        
    def visitProgram(self, ctx:DecafParser.ProgramContext):
        #print('Start')
        self.st.enterScope()
        line_num = ctx.start.line

        self.visitChildren(ctx)

        #3
        main_exists = self.st.probe('main')
        if main_exists == None:
            print('Program has no method main')

        self.st.exitScope()
        #print('End')
    
    def visitField_decl(self, ctx:DecafParser.Field_declContext):
        line_num = ctx.start.line
        data_type = ctx.data_type().getText()
        field_decls = ctx.field_arg()
                
        for f in field_decls:
            
            array_size = 1
            field_symbol = self.st.probe(f.getText())
            
            if f.int_literal() != None:
                
                array_size = f.int_literal().getText()

                if int(array_size) <= 0:

                        # 4
                        print('Error on line ' + str(line_num) + ', array \'' + f.ID().getText() + '\' must have a declaration value greater than 0')

            if field_symbol != None:

                # 1
                print('Error on line', line_num,', variable \'', f.ID().getText(),'\' has already been declared on line ' + str(field_symbol.line))
                
            else:

                field_symbol = VarSymbol(id=f.ID().getText(),
                                         type=data_type,
                                         line=line_num,
                                         size=8 * int(array_size),
                                         mem=HEAP)
                
                self.st.addSymbol(field_symbol)
                        
        self.visitChildren(ctx)
        
    def visitMethod_decl(self, ctx: DecafParser.Method_declContext):
        #Makes method have its own scope
        #self.st.enterScope()
        line_num = ctx.start.line
        method_name = ctx.ID().getText()
        method_args = []

        main_check = self.st.probe('main')
        method_symbol = self.st.probe(method_name)

        if ctx.data_type() != None:
            data_type = ctx.data_type().getText()
        else:
            data_type = "void"

        if method_name == "main" and len(ctx.method_arg()) > 0:
            # 3
            print('Error on line', line_num, ', method \'main\' cannot have any parameters')

        if main_check != None:
           # 3
           print('Warning detected function '+ method_name + ' declared after main, this will not be executed')

        # Adds space to method arguments
        for m in ctx.method_arg():
            method_args.append(m.data_type().getText() + ' ' + m.ID().getText())
            # var_symbol = VarSymbol(id=m.ID().getText(),
            #                          type=m.data_type().getText(),
            #                          line=line_num,
            #                          size=8,
            #                          mem=STACK)
            #
            # self.st.addSymbol(var_symbol)

        method_symbol = MethodSymbol(id=method_name,
                                     type=data_type,
                                     line=line_num,
                                     params=method_args)

        self.st.addSymbol(method_symbol)

        self.visitChildren(ctx)

        statements = ctx.block().statement()

        # 7 and 8
        for s in statements:
            var_type = self.visit(s.expr(0))
            #print(ctx.data_literal().bool_literal())

            if s.RETURN() != None:
                if ctx.VOID() != None:
                    print('Error on line ' + str(line_num) + ', method should not have a return statement')
                #TODO
                # elif ctx.data_type().bool_literal.getText() == var_type:
                #     print('Error on line ' + str(line_num) + ', return value is does not have same type \'' + var_type + '\' as method')

        #self.st.exitScope()
        
    def visitMethod_arg(self, ctx: DecafParser.Method_argContext):
        line_num = ctx.start.line
        data_type = ctx.data_type().getText()
        var_decls = ctx.ID().getText()
        var_symbol = self.st.probe(var_decls)

        if var_symbol != None:
            # 1
            print('Error on line', line_num,', variable \'', var_decls,'\' has already been declared on line ' + str(var_symbol.line))
                            
        else:

            print(var_decls)
            var_symbol = VarSymbol(id=var_decls,
                                     type=data_type,
                                     line=line_num,
                                     size=8,
                                     mem=STACK)
                            
            self.st.addSymbol(var_symbol)
        
        
        self.visitChildren(ctx)
        
    def visitField_arg(self, ctx: DecafParser.Field_argContext):
                
        self.visitChildren(ctx)
        
    def visitData_type(self, ctx: DecafParser.Data_typeContext):
        
        self.visitChildren(ctx)

    def visitBlock(self, ctx: DecafParser.BlockContext):
        line_num = ctx.start.line
        #var_decl = ctx.var_decl(0).getText()
        #self.st.probe(var_decl)
        
        self.visitChildren(ctx)
        
    def visitVar_decl(self, ctx: DecafParser.Var_declContext):
        line_num = ctx.start.line
        var_ids = ctx.ID()
        data_type = ctx.data_type().getText()

        for v in var_ids:
        
            id_symbol = self.st.probe(v.getText())
        
            if id_symbol != None:

                # 1
                print('Error on line ' + str(line_num) + ', variable \'' + v.getText() + '\' has already been declared on line ' + str(id_symbol.line))
            
            else:

                id_symbol = VarSymbol(id=v.getText(),
                                       type=data_type,
                                       line=line_num,
                                       size=8,
                                       mem=STACK)

                self.st.addSymbol(id_symbol)

        self.visitChildren(ctx)
        
    def visitStatement(self, ctx: DecafParser.StatementContext):
        line_num = ctx.start.line
        expression = ctx.expr(0)

        # 11 Expr of an if must have type bool
        if ctx.IF() != None:
            expr_type = self.visit(expression)
            expr_b_type = self.visit(expression.expr(0))

            print(expr_b_type)
            #if (expr_a_type != None and expr_a_type != 'boolean') or (expr_b_type != None and expr_b_type != 'boolean'):
                #print('Error on line ' + str(line_num) + ', expression in if must be of type boolean')

        elif ctx.location() != None:

            loc_type = self.visit(ctx.location())
            expr_type = self.visit(ctx.expr(0))
            operator = ctx.assign_op().getText()
            identifier = self.st.probe(ctx.location().getText())

            #2
            if identifier == None:
                print('Error on line ' + str(line_num) + ', identifier \'' + ctx.location().getText() + '\' has not been declared')

            #16 - TODO change error message
            elif loc_type != None:
                if (loc_type != 'int' or expr_type != 'int') and (operator == '-=' or operator == '+='):
                    print('Error on line ' + str(line_num) + ' variables must be of type int when in an incrementing/decrementing assignment')

                #15
                elif loc_type != expr_type:
                    print('Error on line ' + str(line_num) + ' type mismatched in expression')

        #17
        elif ctx.FOR() != None:

            expr_type_a = self.visit(ctx.expr(0))
            expr_type_b = self.visit(ctx.expr(1))

            if expr_type_a != 'int' or expr_type_b != 'int':

                print('Error on line ' + str(line_num) + ' for statement expressions must be of type int')

        else:

            self.visitChildren(ctx)

    def visitLocation(self, ctx: DecafParser.LocationContext):
        line_num = ctx.start.line
        var_id = ctx.ID().getText()
        var_symb = self.st.lookup(var_id)
        loc_type = ''

        # 10 - Check if statement has square bracket is an array
        if ctx.LSQUARE():
            # 10i
            if var_symb != None and var_symb.size == 8:
                print('Error on line ' + str(line_num) + ', array variable \'' + var_id + '\' is not an array')

            # 10ii
            print(ctx.expr().location().ID())
            if ctx.expr().data_literal() == None:
                print('Error on line ' + str(line_num) + ', array variable \'' + var_id + '\' value must be of type integer')

        if var_symb != None:
            loc_type = var_symb.type

        self.visitChildren(ctx)

        return loc_type
        
    def visitExpr(self, ctx:DecafParser.ExprContext):
        line_num = ctx.start.line
        expr_type = ""

        if len(ctx.expr()) == 2:
            
            type_a = self.visit(ctx.expr(0))
            type_b = self.visit(ctx.expr(1))
            op = ctx.bin_op()

            if type_a == type_b:
                expr_type = type_a
                
            else:
                expr_type = None
                #print('Error on line', line_num, 'type mismatched in expression')

            #12
            if (op.rel_op() != None or op.arith_op()  != None) and type_a != 'int' and type_b != 'int':
                print('Error on line ' + str(line_num) + ' operands must be of type int')
            #13
            elif op.eq_op() != None and type_a != type_b:
                print('Error on line ' + str(line_num) + ' operands must be of same type')
            #14
            elif op.cond_op() != None and (type_a != 'boolean' or type_b != 'boolean'):
                print('Error on line ' + str(line_num) + ' operands must be of type boolean')
            
        elif ctx.location() != None:
            
            var_name = ctx.location().ID().getText()
            var_symbol = self.st.lookup(var_name)

            if var_symbol != None:
                expr_type = var_symbol.type
                
            else:
                #2
                expr_type = None
                print('Error on line ' + str(line_num) + ', ' + var_name + ' has not been declared')

        elif ctx.data_literal() != None:

            if ctx.data_literal().int_literal() != None:
                expr_type = 'int'

            elif ctx.data_literal().bool_literal() != None:
                expr_type = 'boolean'

            else:
                expr_type = None

        elif ctx.method_call() != None:

            method_name = ctx.method_call().method_name().getText()
            method_symbol = self.st.lookup(method_name)

            if method_symbol != None:

                expr_type = method_symbol.type
                self.visit(ctx.method_call())

            else:
                method_symbol = None

        elif ctx.EXCLAMATION() != None:

            expr_type = self.visit(ctx.expr(0))

            #14
            if expr_type != 'boolean':
                print('Error on line ' + str(line_num) + ' operand must be of type boolean')

        else:
            self.visitChildren(ctx)

        return expr_type

    def visitMethod_call(self, ctx:DecafParser.Method_callContext):
        line_num = ctx.start.line
        method_name = ctx.method_name()
        method_symbol = self.st.probe(method_name.getText())

        # 6
        # Check method is of type bool or int
        if method_symbol != None and method_symbol.type == 'void':
            # 6
            print('Error on line ' + str(line_num) + ' method \'' + method_name.getText() + '\' must return a value')

        # 5
        if method_symbol != None:
            # Check correct number of args
            if len(method_symbol.params) != len(ctx.expr()):
                print('Error on line ' + str(line_num) + ' method ' + method_name.getText() + ' needs ' + str(len(method_symbol.params)) + ' arguments has ' + str(len(ctx.expr())))

            else:
                #Check correct types of args
                for i in range(len(method_symbol.params)):
                    param_type = method_symbol.params[i].split(' ')[0]
                    if (param_type == 'int' and ctx.expr(i).data_literal().int_literal() == None) or (param_type == 'boolean' and ctx.expr(i).data_literal().bool_literal() == None):
                        print('Error on line ' + str(line_num) + ' type mismatch on method \'' + method_name.getText() + '\' parameters')

        self.visitChildren(ctx)

filein = open('testdata/semantics/illegal-09.dcf', 'r')
#filein = open('test.dcf', 'r')
lexer = DecafLexer(ant.InputStream(filein.read()))

stream = ant.CommonTokenStream(lexer)

parser = DecafParser(stream)
tree = parser.program()

visitor = DecafSemanticChecker()
visitor.visit(tree)
