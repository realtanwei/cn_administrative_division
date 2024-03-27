
class AdministrativeDivision:
    
    def __init__(self, id, sup_code, data_code, 
                 data_name, data_level, data_order):
        self.id = id
        self.sup_code = sup_code
        self.data_code = data_code
        self.data_name = data_name
        self.pinyin_code = ''
        self.data_level = data_level
        self.data_order = data_order
        self.is_show = 1
        self.can_select = 1
        self.children = []
        self.gb_code_url = ''
        self.class_code = ''

    def to_dict(self):  
        return {'data_name': self.data_name, 'data_code': self.data_code, 'children': self.children}
    