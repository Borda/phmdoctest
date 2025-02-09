# This is Markdown file setup.md

#### This will be the setup code.
The setup logic makes the names assigned here global to the test module.
The code assigns the names math, mylist, a, b, and the function doubler().
Use phmdoctest --setup FIRST to select it.
Setup code does not have an output block. 
```python
import math

mylist = [1, 2, 3]
a, b = 10, 11

def doubler(x):
    return x * 2
```

#### This test case shows the setup names are visible
```python
print("math.pi=", round(math.pi, 3))
print(mylist)
print(a, b)
print("doubler(16)=", doubler(16))
```
expected output:
```
math.pi= 3.142
[1, 2, 3]
10 11
doubler(16)= 32
```

#### This test case modifies mylist.
The objects created by the --setup code can be modified
and blocks run afterward will see the changes.  
```python
mylist.append(4)
print(mylist)
```
expected output:
```
[1, 2, 3, 4]
```

#### This test case sees the modified mylist.
```python
print(mylist == [1, 2, 3, 4])
```
expected output:
```
True
```

#### This will be specified as the teardown code.
Use phmdoctest --teardown LAST to select it.
Teardown code does not have an output block. 
```python
mylist.clear()
assert not mylist, "mylist was not emptied"
```