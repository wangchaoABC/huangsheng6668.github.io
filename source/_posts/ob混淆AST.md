---
title: ob混淆AST
date: 2020-08-28 17:42:12
tags: JS逆向
categories: JS逆向
---

#### ob混淆的特征
大数组+位移函数+解密函数，多个位置多次调用解密函数。
![picture 1](http://img.juziss.cn/d0c6859180be2f7d568f6c8b78c5885fab00053b6259fdd62dbd9f5fc8156940.png)  

#### 写AST
![picture 2](http://img.juziss.cn/150d90ddafa0b40fbe1fff8bc13c59c6d30a01924a30c173534df6c41480e5cc.png)  
自执行函数如果带参数的都会有个加载器，我们看看兄弟节点有啥用吧。
![picture 3](http://img.juziss.cn/9600215eeb2fce85175acc8a7801854d01e858379f3b9583740754c4e1a8a29c.png)  
这些setCookie这类的只是为某个obj的属性。只需观察这些函数里面有没有啥实参。

![picture 4](http://img.juziss.cn/ef87660bef2ed82824f11b6ae8b6b22065f0233cf5093115e5e30985e560f4d5.png)  

对这个自执行的函数来说，全局的变量只有这么两个`_0x1032, 0x1a7`,就围绕这两个看看。
![picture 5](http://img.juziss.cn/e9e7da3a3ee368f50ba2fa476eff801fd03c7062e3f93117e7d795773c92c078.png)  
这两个实参到这个函数里是`_0x263f33,_0x270f13`.

JS的函数的参数是啥传递。
![picture 7](http://img.juziss.cn/fe02fe826e7a1a85b95228c5838471ca10c6d495449c89430ae6a2754f438da0.png)  


也就是说，如果**不通过属性来修改对象的值，那都不影响实参**！！！

我们来看看这个函数里有哪里用到了实参。

![picture 1](http://img.juziss.cn/42feccf893bab40460cec78e35e3c61bf79391d84c769672af95994e99c7cf7e.png)  

只有这一处使用到了实参，数组实参只有加载器用到。

步进看看该函数是干啥的。
![picture 2](http://img.juziss.cn/23ca41a8baa3295a3134664f4e088bad5460a6e24e8705a68433497428f76356.png)  
执行的函数是加载器，加载器的作用也只是为了执行参数而已。也就是说，其实整段代码其实也就只有++那段有用。

![picture 3](http://img.juziss.cn/4666c13bb4562c84808f6a86832eb87babb491ca1f866d22bb0b2c277db37e74.png)  
也就是这段。只需把函数名改为加载器的函数名，参数改为形参的参数名即可。

我们可以手动删掉，也可以通过AST来删。这里我们来用AST。

接下来我们来分析一下解密函数。
![picture 4](http://img.juziss.cn/9cc89370500009575b2f5e32bb0887b27534efeb7b67a81f695dc696e56bebe2.png)  
我们看到用到`_0x270f13`只有一处。
再看rc4这函数是啥。
![picture 5](http://img.juziss.cn/301e64eac4f52c3e60bb12aa48b1d541989afd2317f162f24e35e09678391b06.png)  

保留了以上提到的，后面这里===undefine处，仅仅只需保留
![picture 6](http://img.juziss.cn/ca9020e8b04940bfcc8983d93bd9d315f39ca73b8172e5981e63d41b4d0c2831.png)  
该处即可。

##### 控制流平坦化

![picture 7](http://img.juziss.cn/0b7f6d4ea09ffa22aa2305ff503cee28395ff2632300e3fa2222b3e1846c7054.png)  
像这种通过switch和while来混淆代码的执行顺序，既是控制流平坦化，这类的代码比较麻烦，不过可以看看极验那块的代码，那块的控制流平坦化比ob混淆的要好些，这个相对简单，直接附上代码。
```js
const decode_while = {
    WhileStatement(path) {
        let {test, body} = path.node;
        let swithchNode = body.body[0];
        if (!types.isUnaryExpression(test) || !types.isSwitchStatement(swithchNode)) return;
        let {discriminant, cases} = swithchNode;
        if (!types.isMemberExpression(discriminant) || !types.isUpdateExpression(discriminant.property)) return;
        let arrayName = discriminant.object.name;
        let per_bro_node = path.getAllPrevSiblings();
        let array = []
        per_bro_node.forEach(per_node => {
            const {declarations} = per_node.node;
            let {id, init} = declarations[0];
            if (arrayName === id.name) {
                array = init.callee.object.value.split('|');
            }
            per_node.remove();
        });

        let replace_body = [];
        array.forEach(index => {
                let case_body = cases[index].consequent;
                if (types.isContinueStatement(case_body[case_body.length - 1])) {
                    case_body.pop();
                }
            replace_body = replace_body.concat(case_body);
            }
        );
        path.replaceInline(replace_body);
    }
}

traverse(ast, decode_while);
```

完整代码：
```js
/***********************************************************
 ob混淆这类的特征是大数组加位移函数加解密函数
 ***********************************************************/


const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");
const generator = require("@babel/generator").default;
const fs = require('fs');
decode_file = 'D:\\huangsheng\\self\\js_workspace\\node_workspace\\js_parse\\bitstamp\\js\\result.js'
var jscode = fs.readFileSync('D:\\huangsheng\\self\\js_workspace\\node_workspace\\js_parse\\bitstamp\\js\\source.js', "utf-8", function (err, data) {
    if (err) {
        console.log(err);
    } else {
        code = data.toString();
    }
});
let ast = parser.parse(jscode)

/***********************************************************
 NumericLiteral ---> Literal
 StringLiteral  ---> Literal
 用于处理已十六进制显示的字符串或者数值
 ***********************************************************/
const delete_extra =
    {
        "NumericLiteral|StringLiteral": function (path) {
            delete path.node.extra;
        },
    }

traverse(ast, delete_extra);

// 删除加载器下的多余的节点
const decode_str = {
    VariableDeclarator(path) {
        let {id, init} = path.node;
        if (!types.isArrayExpression(init) || init.elements.length == 0) return;
        let code = path.toString();

        let second_sibling = path.parentPath.getNextSibling(); //获取移位函数节点
        let third_sibling = second_sibling.getNextSibling();   //获取解密函数节点

        // 开始检测特征
        if (!types.isExpressionStatement(second_sibling) || !types.isVariableDeclaration(third_sibling)) return;
        let expression = second_sibling.get('expression');
        if (!expression.isCallExpression()) return;

        let {callee, arguments} = expression.node;
        if (arguments.length !== 2 ||
            !types.isFunctionExpression(callee) ||
            !types.isIdentifier(arguments[0], {name: id.name}) ||
            !types.isNumericLiteral(arguments[1])
        ) return;

        let {declarations} = third_sibling.node;

        if (!declarations ||
            declarations.length !== 1 ||
            !types.isFunctionExpression(declarations[0].init)
        ) return;

        // 检测结束
        let sourceSecond = second_sibling.toString()
        let thirdFuncName = third_sibling.node.declarations[0].id.name;
        // 开始处理移位函数
        if (sourceSecond.indexOf('removeCookie') !== -1) {
            let second_arg_node = callee.params[1];
            let body = callee.body.body;
            let call_fun = body[0].declarations[0].id;  //解密函数的函数名，用于遍历其作用域
            body.pop();
            body.pop();
            body.push(types.ExpressionStatement(types.UpdateExpression("++", second_arg_node)));
            body.push(types.ExpressionStatement(types.callExpression(call_fun, [second_arg_node])));

            // 位移函数处理结束

            // 处理解密函数开始
            let end = third_sibling.node.end; //防止遍历函数体里的调用
            third_sibling.traverse({
                AssignmentExpression(path_) {
                    let left = path_.get('left');
                    let leftCode = left.toString()
                    let right = path_.get('right');
                    let rightCode = right.toString();
                    if (rightCode.indexOf(thirdFuncName) === -1 || rightCode.indexOf(leftCode) === -1) return;
                    let ifParantNode = path_.findParent(g => {
                        return g.isIfStatement();
                    });
                    ifParantNode && ifParantNode.replaceWith(path_.node);
                }
            });
            code += ';!' + second_sibling.toString() + third_sibling.toString();
            //eval到本地环境
            eval(code);

            const binding = third_sibling.scope.getBinding(thirdFuncName);
            if (!binding || binding.constantViolations.length > 0) return;

            let can_removed = true;
            for (const temp of binding.referencePaths) {
                // 为了处理调用解密函数处，修改为常量，故不能调用到解密函数中
                if (temp.node.start < end) {
                    continue;
                }
                let callPath = temp.findParent(p => {
                    return p.isCallExpression();
                });
                try {
                    let fun_value = eval(callPath.toString());
                    console.log('del with fun:', callPath.toString(), '  is value:', fun_value);
                    callPath && callPath.replaceWith(types.valueToNode(fun_value));
                } catch (e) {
                    can_removed = false;
                }
            }
            if (can_removed) {
                path.parentPath.remove();
                second_sibling.remove();
                third_sibling.remove();
            }
        }
    }
}

traverse(ast, decode_str);

// 处理BinaryExpression
const decode_binary = {
    BinaryExpression(path) {
        const {confident, value} = path.evaluate();
        if (Infinity === value) return;
        confident && path.replaceWith(types.valueToNode(value));
    }
}

traverse(ast, decode_binary);

// 处理控制流平坦化
const decode_while = {
    WhileStatement(path) {
        let {test, body} = path.node;
        let swithchNode = body.body[0];
        if (!types.isUnaryExpression(test) || !types.isSwitchStatement(swithchNode)) return;
        let {discriminant, cases} = swithchNode;
        if (!types.isMemberExpression(discriminant) || !types.isUpdateExpression(discriminant.property)) return;
        let arrayName = discriminant.object.name;
        let per_bro_node = path.getAllPrevSiblings();
        let array = []
        per_bro_node.forEach(per_node => {
            const {declarations} = per_node.node;
            let {id, init} = declarations[0];
            if (arrayName === id.name) {
                array = init.callee.object.value.split('|');
            }
            per_node.remove();
        });

        let replace_body = [];
        array.forEach(index => {
                let case_body = cases[index].consequent;
                if (types.isContinueStatement(case_body[case_body.length - 1])) {
                    case_body.pop();
                }
            replace_body = replace_body.concat(case_body);
            }
        );
        path.replaceInline(replace_body);
    }
}

traverse(ast, decode_while);

/************************************
 处理完毕，生成新代码
 *************************************/
let {code} = generator(ast);
fs.writeFile(decode_file, code, (err) => {
});

```