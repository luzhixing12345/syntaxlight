
# EBNF

任何一种编程语言都需要通过一组规则作为有限集合, 而这需要通过某种方式来组成这种语法

EBNF(**E**xtended **B**ackus-**N**aur **F**orm 扩展巴科斯范式) 是其中一种. EBNF 通过数学的方式描述编程语言语法, 但他的描述范围不局限于编程领域, 同时也它也是 CFG(**C**ontext-**F**ree **G**rammar 上下文无关文法) 的一种.

一般来说 EBNF 由以下三部分组成

- 终结符(terminal) 的集合
- 非终结符(non-terminal) 的集合
- 产生式(production) 的集合

终结符是指 **语句中不能被继续拆解的基本单位**. 一把来说终结符是指词法分析器返回的结果 token

非终结符可以理解为一个组合情况,相当于一个小函数.非终结符可以由终结符组成,也可以由其他非终结符组成

产生式是由一组非终结符或终结符按照一定的规则组合而成的

## 参考

- [BNF](https://zh.wikipedia.org/wiki/%E5%B7%B4%E7%A7%91%E6%96%AF%E8%8C%83%E5%BC%8F)
- [EBNF](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form)
- https://blog.csdn.net/lin_strong/article/details/78583543