$.validator.addMethod('format_check', function(value, element, reg_param){
    return this.optional(element) || reg_param.test(value);
}, '格式验证不通过');
