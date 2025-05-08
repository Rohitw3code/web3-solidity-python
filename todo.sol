// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract TodoList{
     struct Todo{
        string task;
        bool completd;
     }

     Todo[] public todos;

     event TodoAdded(uint indexed todoId,string task);

     function addTodo(string memory _task) public {
        todos.push(Todo(_task,false));
        uint todoId = todos.length-1;
        emit TodoAdded(todoId,_task);
     }

     function getTodo(uint _index) public view returns (string memory,bool){
        Todo memory todo = todos[_index];
        return (todo.task,todo.completd);       
     }

     function getAllTodo() public view returns (Todo[] memory){
        return todos;
     }

}