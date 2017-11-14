/*

* Cis2750 F2017

* Assignment 0

* Greg Hetherington 0936504

* file contains a Doubly Linked List API with all the methods fro mthe header file

* Resources:

    -Data Structures (Cis2520) with fangji Wang
    -Cis2750 Lectures with Denis Nikitenko
    -Stackoverflow.com
    -tutoriaalpoint.com

*/

#include "LinkedListAPI.h"

List initializeList(char* (*printFunction)(void *toBePrinted),void (*deleteFunction)(void *toBeDeleted),int (*compareFunction)(const void *first,const void *second)) {
    List newListHead;

    newListHead.head = NULL;
    newListHead.tail = NULL;
    newListHead.length = 0;
    newListHead.printData = printFunction;
    newListHead.deleteData = deleteFunction;
    newListHead.compare = compareFunction;

    return newListHead;
}

Node *initializeNode(void *data) {
    if (data != NULL) {
        Node* newListNode;

        newListNode = ( struct listNode* )malloc( sizeof( *newListNode));
        newListNode->data = data;
        newListNode->next = NULL;
        newListNode->previous = NULL;

        return newListNode;
    } else {
        return NULL;
    }
}

void insertFront(List *list, void *toBeAdded) {
    if (list != NULL) {
        list->length++;
        Node* newNode = initializeNode(toBeAdded);
        if (list->head == NULL) {
            list->head = newNode;
            list->tail = newNode;
        } else {
            list->head->previous = newNode;
            newNode->next = list->head;
            list->head = newNode;
            newNode->previous = NULL;
        }
    }
}

void insertBack(List *list, void *toBeAdded) {
    if (list != NULL) {
        list->length++;
        Node* newNode = initializeNode(toBeAdded);
        if (list->head == NULL) {
            list->head = newNode;
            list->tail = newNode;
        } else {
            newNode->previous = list->tail;
            list->tail->next = newNode;
            list->tail = newNode;
            newNode->next = NULL;
        }
    }
}

void clearList(List *list) {
    if (list != NULL) {
        Node* current = list->head;
        Node* next;
        list->head = NULL;
        list->tail = NULL;
        while (current != NULL) {
            next = current->next;
            free(current);
            current = next;
        }
    }
}

void insertSorted(List *list, void *toBeAdded) {
    if (list != NULL) {    
    Node* newNode = initializeNode(toBeAdded);
    if (list->head == NULL) {
        list->head = newNode;
        list->tail = newNode;
    } else {
        Node* current = list->head;
        if (current != NULL && list->compare(newNode->data, current->data) < 0) {
            list->head = newNode;
            newNode->next = current;
            current->previous = newNode;
        } else {
            while (current->next != NULL && list->compare(newNode->data, current->next->data) > 0) {
                current = current->next;
            }
            if (current->next == NULL) {
                list->tail = newNode;
            } else {
                newNode->next = current->next;
                current->next->previous = newNode;
            }
            newNode->previous = current;
            current->next = newNode;
        }
    }
    }
}

void* deleteDataFromList(List *list, void *toBeDeleted) {
    if (list != NULL && toBeDeleted != NULL) {
        Node* current = list->head;
        while (current != NULL) {
            if (list->compare(current->data, toBeDeleted) == 0) {
                list->length--;
                if (current->previous == NULL) {
                    list->head = list->head->next;
                }
                if (current->previous != NULL) {
                    current->previous->next = current->next;
                }
                if (current->next != NULL) {
                    current->next->previous = current->previous;
                }
                if (current->next == NULL) {
                    list->tail = list->tail->previous;
                }
                void* returnData = current->data;
                //free(current);
                return returnData;
            }
            current = current->next;
        }
    }
    return NULL;
}

void* getFromFront(List list) {
    if (list.head != NULL) {
        return list.head->data;
    }
    return NULL;
}

void* getFromBack(List list) {
    if (list.head != NULL) {
        return list.tail->data;
    }
    return NULL;
}

char* toString(List list) {
    if (list.head != NULL) {
        char* returnString = malloc(1000);
        Node* current = list.head;
        while(current != NULL) {
            char* stringOfCurrent = list.printData(current->data);
            strcat(returnString, stringOfCurrent);
            current = current->next;
        }
        return returnString;
    } else {
        return "empty list";
    }
}

ListIterator createIterator(List list) {
    if (list.head != NULL) {
        ListIterator listIter;
        listIter.current = list.head;
        return listIter;
    } else {
        ListIterator listIter;
        return listIter;
    }
}

void* nextElement(ListIterator* iter) {
    if (iter != NULL && iter->current != NULL) {
        void* data = iter->current->data;
        iter->current = iter->current->next;
        return data;
    }
    return NULL;
}

int getLength(List list) {
    if (list.length >= 0 && list.length < 999) {
        return list.length;
    }
    return -1;
}

void* findElement(List list, bool (*customCompare)(const void* first,const void* second), const void* searchRecord) {
    if (list.head != NULL && customCompare != NULL) {
        Node* node = list.head;
        for (int i = 0; i < list.length; i++) {
            if (customCompare(node->data, searchRecord)) {
                return node->data;
            }
            node = node->next;
        }
    }
    return NULL;
}
