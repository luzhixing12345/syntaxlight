
# dot
## [1.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/1.dot)

```dot
digraph G{
        size="6!" ratio=fill
        node [shape=circle, style=bold, fontsize=22, fontname=Consolas, width=0.8, height=0.8]
        edge [style=bold]
        label="(41) select 3"
        node0[label="26"]
        node1[label="25"]
        node2[label="17"]
        node3[label="3"]
        node4[label="19"]
        node5[label="7"]
        node6[label="1"]
        node7[label="2"]
        node0 -> node1
        n100[width=0.1, height=0.1, shape=point, style=invis]
        node0 -> n100[weight=10, style=invis]
        node0 -> node2
        node1 -> node3
        n101[width=0.1, height=0.1, shape=point, style=invis]
        node1 -> n101[weight=10, style=invis]
        node1 -> node4
        node2 -> node5
        n102[width=0.1, height=0.1, shape=point, style=invis]
        node2 -> n102[weight=10, style=invis]
        node2 -> node6
        node3 -> node7
}
```
## [2.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/2.dot)

```dot
digraph astgraph {
  node [shape=circle, fontsize=12, fontname="Courier", height=.1];
  ranksep=.3;
  edge [arrowsize=.5]
  node1 [label="+"]
}
```
## [3.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/3.dot)

```dot
digraph Alf {
size = "6,9";
node [ shape = record ];
Decl [ label = "\n\nDecl|{name|access|decl_flags|extern_c_linkage}"];
Nontype_decl [ label = "Nontype_decl|{type}"];
Defined_decl [ label = "Defined_decl|{linkage}"];
Data_decl [ label = "Data_decl|{storage_class}"];
Function_decl [ label = "Function_decl|{formals|defaults}"];
Data [ label = "Data|{initializer}"];
Function [ label = "Function|{body}"];
Constructor [ label = "Constructor|{member_initializers}"];
Aggregate ->  Type_decl ;
Class -> Aggregate;
Union -> Aggregate;
Data -> Data_decl;
Data -> Defn;
Data_decl -> Defined_decl;
Data_member ->  Nontype_decl ;
Defined_decl -> Nontype_decl;
Defn -> Defined_decl;
Enum ->  Type_decl ;
Enumerator ->  Nontype_decl ;
Function -> Defn;
Function -> Function_decl;
Constructor -> Function;
Destructor -> Function;
Function_decl -> Defined_decl;
Nontype_decl ->  Decl ;
Template_type_arg ->  Type_decl ;
Type_decl ->  Decl ;
Typedef ->  Type_decl ;
}

```
## [4.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/4.dot)

```dot
digraph g {
	rankdir=LR;

	node [shape=rpromoter colorscheme=rdbu5 color=1 style=filled fontcolor=3]; Hef1a; TRE; UAS; Hef1aLacOid;
	Hef1aLacOid [label="Hef1a-LacOid"];
	node [shape=rarrow colorscheme=rdbu5 color=5 style=filled fontcolor=3]; Gal4VP16; LacI; rtTA3; DeltamCherry;
	Gal4VP16 [label="Gal4-VP16"];	
	product [shape=oval style=filled colorscheme=rdbu5 color=2 label=""];
	repression [shape=oval label="LacI repression" fontcolor=black style=dotted];
	node [shape=oval style=filled colorscheme=rdbu5 color=4 fontcolor=5];
	combination [label="rtTA3 + Doxycycline"];
	LacIprotein [label="LacI"];
	rtTA3protein [label="rtTA3"];
	Gal4VP16protein [label="Gal4-VP16"];
	

	subgraph cluster_0 {
		colorscheme=rdbu5;
		color=3;
		node [colorscheme=rdbu5 fontcolor=3];
		Hef1a -> Gal4VP16 [arrowhead=none];
		Gal4VP16 -> UAS [arrowhead=none];
		UAS -> LacI [arrowhead=none];
		LacI -> Hef1aLacOid [arrowhead=none];
		Hef1aLacOid -> rtTA3 [arrowhead=none];
		rtTA3 -> TRE [arrowhead=none];
		TRE -> DeltamCherry [arrowhead=none]
	}
	
	Gal4VP16 -> Gal4VP16protein;
	Gal4VP16protein -> UAS;
	LacI -> LacIprotein;
	LacIprotein -> repression;
	repression -> Hef1aLacOid [arrowhead=tee];
	IPTG -> repression [arrowhead=tee];
	rtTA3 -> rtTA3protein;
	rtTA3protein -> combination;
	combination -> TRE;
	Doxycycline -> combination;
	DeltamCherry -> product;
	
	
		
}

```
## [5.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/5.dot)

```dot
digraph G {

	subgraph cluster_0 {
		style=filled;
		color=lightgrey;
		node [style=filled,color=white];
		a0 -> a1 -> a2 -> a3;
		label = "process #1";
	}

	subgraph cluster_1 {
		node [style=filled];
		b0 -> b1 -> b2 -> b3;
		label = "process #2";
		color=blue
	}
	start -> a0;
	start -> b0;
	a1 -> b3;
	b2 -> a3;
	a3 -> a0;
	a3 -> end;
	b3 -> end;

	start [shape=Mdiamond];
	end [shape=Msquare];
}

```
## [6.dot](https://github.com/luzhixing12345/syntaxlight/tree/main/test/dot/6.dot)

```dot
digraph G {
	nodesep=.05;
	rankdir=LR;
	node [shape=record,width=.1,height=.1];

	node0 [label = "<f0> |<f1> |<f2> |<f3> |<f4> |<f5> |<f6> | ",height=2.0];
	node [width = 1.5];
	node1 [label = "{<n> n14 | 719 |<p> }"];
	node2 [label = "{<n> a1  | 805 |<p> }"];
	node3 [label = "{<n> i9  | 718 |<p> }"];
	node4 [label = "{<n> e5  | 989 |<p> }"];
	node5 [label = "{<n> t20 | 959 |<p> }"] ;
	node6 [label = "{<n> o15 | 794 |<p> }"] ;
	node7 [label = "{<n> s19 | 659 |<p> }"] ;

	node0:f0 -> node1:n;
	node0:f1 -> node2:n;
	node0:f2 -> node3:n;
	node0:f5 -> node4:n;
	node0:f6 -> node5:n;
	node2:p -> node6:n;
	node4:p -> node7:n;
}

```
