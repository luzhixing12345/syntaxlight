
# xml
## [1.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/1.xml)

```xml
<catalog>
  <book>
    <title>Harry Potter <name>Product A</name> and the Philosopher's Stone</title>
    <author>J.K. Rowling</author>
    <year>1997</year>
  </book>
  <book>
    <title>The Great Gatsby</title>
    <author>F. Scott Fitzgerald</author>
    <year>1925</year>
  </book>
</catalog>

```
## [2.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/2.xml)

```xml
<contacts>
  <contact>
    <name>John Doe</name>
    <email>john.doe@example.com</email>
    <phone>1234567890</phone>
  </contact>
  <contact>
    <name>Jane Smith</name>
    <email>jane.smith@example.com</email>
    <phone>9876543210</phone>
  </contact>
</contacts>

```
## [3.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/3.xml)

```xml
<order id="12345" date="2023-07-10">
  <customer>
    <name>John Doe</name>
    <address>
      <street>Main Street</street>
      <city>Cityville</city>
      <country>Countryland</country>
    </address>
  </customer>
  <items>
    <item id="1">
      <name>Product A</name>
      <price>19.99</price>
      <quantity>2</quantity>
    </item>
    <item id="2">
      <name>Product B</name>
      <price>9.99</price>
      <quantity>3</quantity>
    </item>
  </items>
</order>

```
## [4.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/4.xml)

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<article>
  <title>Introduction to XML Parsing</title>
  <author>Jane Smith</author>
  <content>
    XML parsing is a fundamental skill for working with structured data. It involves extracting information from XML documents and processing it.
  </content>
  <comments>
    <comment>
      <author>John Doe</author>
      <date>2023-07-05</date>
      <text>Great article! I learned a lot.</text>
    </comment>
    <comment>
      <author>Jane Smith</author>
      <date>2023-07-07</date>
      <!-- <text>Thank you, John! I'm glad you found it helpful.</text> -->
    </comment>
  </comments>
</article>

```
## [5.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/5.xml)

```xml
<!-- <text>Thank you, John! I'm glad you found it helpful.</text> -->
<comment>
      <author>John Doe</author>
      <date>2023-07-05</date>
      <text>Great article! I learned a lot.</text>
      <name><book /></name>
    </comment>
    
```
## [6.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/6.xml)

```xml
<items>
    <item id="1">
      <name>Product A</name>
      <price>19.99</price>
      <quantity>2</quantity>
    </item>
    <item id="2">
      <name>Product B</name>
      <price>9.99</price>
      <quantity>3</quantity>
    </item>
  </items><
```
## [7.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/7.xml)

```xml
<items
    <item id="1">
      <name>Product A</name>
      <price>19.99</price>
      <quantity>2</quantity>
    </item>
    <item id="2">
      <name>Product B</name>
      <price>9.99</price>
      <quantity>3</quantity>
    </item>
  </items>
```
## [8.xml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/xml/8.xml)

```xml
<items a23 = 123>
    <item id="1">
      <name>Product A</name>
      <price>19.99</price>
      <quantity>2</quantity>
    </item>
    <item id="2">
      <name>Product B</name>
      <price>9.99</price>
      <quantity>3</quantity>
    </item>
  </items>
```
