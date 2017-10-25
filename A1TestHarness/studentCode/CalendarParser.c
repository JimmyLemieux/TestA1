/*

* Cis2750 F2017

* Assignment 1

* Greg Hetherington 0936504

* file contains a Parser for the iCalendar file format

* Resources:

    -Data Structures (Cis2520) with fangji Wang
    -Cis2750 Lectures with Denis Nikitenko
    -Stackoverflow.com
    -tutoriaalpoint.com

*/

#include "../include/CalendarParser.h"
#include <ctype.h>

int isDateTimeMalformed(char *dateTime) {
    if (dateTime == NULL || strcmp(dateTime, "") == 0) {
        return 0;
    }
    if (dateTime[8] != 'T') {
        return 0;
    }
    for (int i = 0; i < strlen(dateTime); i++) {
        if (i < 8) {
            if (!isdigit(dateTime[i])) {
                return 0;
            }
        } else if (i > 8 && i < 15) {
            if (!isdigit(dateTime[i])) {
                return 0;
            }
        }
    }
    return 1;
}

int isVersionMalformed(char * version) {
    if (version == NULL || strcmp(version, "") == 0) {
        return 0;
    }
    int numberOfDecimals = 0;
    for (int i = 0; i < strlen(version); i++) {
        if (!isdigit(version[i]) && version[i] != '.') {
            return 0;
        } else if (version[i] == '.') {
            numberOfDecimals++;
            if (numberOfDecimals > 1) {
                return 0;
            }
        }
    }
    return 1;
}

char* getFileExtention(char *fileName) {
    char *fileExt = strrchr(fileName, '.');
    if (!fileExt || fileExt == fileName) {
        return "";
    }
    return fileExt + 1;
}

void removeSpacesFromfrontOfString(char *str) {
    int count = 0;
    int isPastFront = 0;
        for (int i = 0; str[i]; i++) {
            if (str[i] != ' ') {
                isPastFront = 1;
                str[count++] = str[i];
            } else if (isPastFront == 1) {
            str[count++] = str[i];
        }
    }
    str[count - 1] = '\0';
}

int isStringOnlySpaces(char *str) {
    int spaceCount = 0;
    for (int i = 0; str[i]; i++) {
        if (str[i] == ' ') {
            spaceCount++;
        }
    }
    if (spaceCount == strlen(str)) {
        return 1;
    } else {
        return 0;
    }
}

int getFileLenght(char *fileName) {
    int fileLenght = 0;
    if (fileName == NULL) {
        return 0;
    }
    FILE *f;
    f = fopen(fileName, "r");
    char line[128];
    if (f == NULL) {
        return 0;
    }                                                
    while (fgets(line, sizeof(line), f) != NULL) {
        for (int i = 0; line[i] != '\0'; i++) {
            if (line[i] == ';') {
                break;
            } else if (line[i] != ' ') {
                removeSpacesFromfrontOfString(line);
                if (isStringOnlySpaces(line) == 0) {
                    fileLenght++;
                }
                break;
            }
        }
    } fclose(f);
    return fileLenght;
}

void propDestroy(void *data) {
    free(data);
}
void alarmDestroy(void *data) {
    Alarm* tmpAlarm;
    tmpAlarm = (Alarm*)data;
    free(tmpAlarm->trigger);
    free(tmpAlarm);
}
char * printAlarm(void *toBePrinted) {
    char* tmpStr;
    Alarm* tmpName;
    int len;
            
    if (toBePrinted == NULL) {
        return NULL;
    }
                            
    tmpName = (Alarm*)toBePrinted;
                               
    len = strlen(tmpName->action)+strlen(tmpName->trigger)+40;
    tmpStr = (char*)malloc(sizeof(char)*len);

    sprintf(tmpStr, "Action:%s Trigger:%s\n", tmpName->action, tmpName->trigger);
    return tmpStr;
}
char * printProp(void *toBePrinted) {
    char* tmpStr;
    Property* tmpName;
    int len;
    
    if (toBePrinted == NULL) {
        return NULL;
    }
    
    tmpName = (Property*)toBePrinted;

    len = strlen(tmpName->propName)+strlen(tmpName->propDescr)+40;
    tmpStr = (char*)malloc(sizeof(char)*len);
    
    sprintf(tmpStr, "Name:%s Descr:%s\n", tmpName->propName, tmpName->propDescr);
    
    return tmpStr;
}
int testCompare(const void * one, const void * two) {
    return strcmp((char*)one, (char*)two);
}


/** Function to create a Calendar object based on the contents of an iCalendar file.
 *@pre File name cannot be an empty string or NULL.  File name must have the .ics extension.
       File represented by this name must exist and must be readable.
 *@post Either:
        A valid calendar has been created, its address was stored in the variable obj, and OK was returned
		or 
		An error occurred, the calendar was not created, all temporary memory was freed, obj was set to NULL, and the 
		appropriate error code was returned
 *@return the error code indicating success or the error encountered when parsing the calendar
 *@param fileName - a string containing the name of the iCalendar file
 *@param a double pointer to a Calendar struct that needs to be allocated
**/
ErrorCode createCalendar(char* fileName, Calendar** obj) {
    //read file
    if (fileName == NULL || strcmp(getFileExtention(fileName), "ics") != 0) {
        return INV_FILE;
    }
    FILE *iCalFile;
    iCalFile = fopen(fileName, "r");        
    
    char line[128];
    if (iCalFile == NULL) {
        return INV_FILE;
    }
    int k = 0;
    int fileLenght = getFileLenght(fileName);
    char** fileContentsData = malloc(fileLenght * sizeof(char *));//malloc
    char** fileContentsType = malloc(fileLenght * sizeof(char *));//malloc
    
    while (fgets(line, sizeof(line), iCalFile) != NULL) {
        for (int i = 0; line[i] != '\0'; i++) {
            if (line[i] == ';') {
                break;
            } else if (line[i] != ' ') {
                removeSpacesFromfrontOfString(line);
                if (isStringOnlySpaces(line) == 0) {
                    char* type = malloc((strlen(line) + 1) * sizeof(char));//malloc
                    char* data = malloc((strlen(line) + 1) * sizeof(char));//malloc
                    int c = 0;
                    for(int i = 0; i <= strlen(line); i++) {
                        if (c != 0 && line[i] != '\0') {
                            data[i-c-1] = line[i];
                        } else if ((line[i] == ';' || line[i] == ':') && c == 0) {
                            type[i] = '\0';
                            c = i;
                        } else if (line[i] == '\0') {
                            data[i-c-2] = '\0';
                            break;
                        } else {
                            line[i] = toupper(line[i]);
                            type[i] = line[i];
                        }
                    }
                    fileContentsType[k] = malloc((strlen(type) + 1) * sizeof(char));//malloc looped
                    strcpy(fileContentsType[k], type);
                    
                    fileContentsData[k] = malloc((strlen(data) + 1) * sizeof(char));//malloc looped
                    strcpy(fileContentsData[k], data);
                                        
                    //printf("{%s}\n", line);
                    //printf("Type: {%s},Data: {%s}\n", fileContentsType[k], fileContentsData[k]);
                    
                    k++;
                    free(type);
                    free(data);
                }
                break;
            }
        }
    }
    fclose(iCalFile);

    if (strcmp(fileContentsType[0], "BEGIN") != 0 || strcmp(fileContentsData[0], "VCALENDAR") != 0) {
        return INV_CAL;
    }
    
    Calendar* cal = malloc(sizeof(Calendar));
    
    ErrorCode returnCode = INV_CAL;
    int isTrigger = 0;
    char **state = malloc(10 * sizeof(char *));//malloc
    int stateNum = 0;
    state[stateNum] = "NONE";

    for (int i = 0; i < fileLenght; i++) {
        //printf("State:{%s},Type:{%s},Data:{%s}\n", state[stateNum], fileContentsType[i], fileContentsData[i]);
        if (strcmp(fileContentsType[i], "BEGIN") == 0) {
            stateNum++;
            state[stateNum] = malloc((strlen(fileContentsData[i]) + 1) * sizeof(char));
            if (strcmp(fileContentsData[i], "VCALENDAR") == 0) {
                strcpy(state[stateNum], "VCALENDAR");
                cal->version = -1;
                strcpy(cal->prodID, "-1");
                cal->event = malloc(sizeof(Event));
                strcpy(cal->event->UID, "-1");
            } else if (strcmp(fileContentsData[i], "VEVENT") == 0) {
                strcpy(state[stateNum], "VEVENT");
                strcpy(cal->event->UID, "-1");
                strcpy(cal->event->creationDateTime.time, "-1");
                strcpy(cal->event->creationDateTime.date, "-1");
                cal->event->properties = initializeList(printProp, propDestroy, testCompare);
                cal->event->alarms = initializeList(printAlarm, alarmDestroy, testCompare);
            } else if (strcmp(fileContentsData[i], "VALARM") == 0) {
                strcpy(state[stateNum], "VALARM");
                Alarm * newAlarm = malloc(sizeof(Alarm));
                strcpy(newAlarm->action, "-1");
                newAlarm->properties = initializeList(printProp, propDestroy, testCompare);
                insertBack(&cal->event->alarms, newAlarm);
                isTrigger = 0;
            } else {
                strcpy(state[stateNum], "OTHER");
            }
        } else if (strcmp(fileContentsType[i], "END") == 0) {
                if (strcmp(fileContentsData[i], "VCALENDAR") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {
                    //check for missing proporties
                    if (returnCode == INV_CAL) {
                        returnCode = OK;
                        if (cal->version == -1 || strcmp(cal->prodID, "-1") == 0 || strcmp(cal->event->UID, "-1") == 0) {
                            returnCode = INV_CAL;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(fileContentsData[i], "VEVENT") == 0 && strcmp(state[stateNum], "VEVENT") ==0) {
                    //checkfor missing properties
                    if (returnCode == INV_CAL) {
                        if (strcmp(cal->event->UID, "-1") == 0 || strcmp(cal->event->creationDateTime.time, "-1") == 0 || strcmp(cal->event->creationDateTime.date, "-1") == 0) {
                            returnCode = INV_EVENT;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(fileContentsData[i], "VALARM") == 0 && strcmp(state[stateNum], "VALARM") ==0) {
                    //checkfor missing properties
                    Alarm * alarm = getFromBack(cal->event->alarms);
                    if (returnCode == INV_CAL) {
                        if (strcmp(alarm->action, "-1") == 0 || isTrigger == 0) {
                            returnCode = INV_EVENT;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(state[stateNum], "OTHER") == 0) {
                    free(state[stateNum]);
                    stateNum--;                    
                } else {
                    returnCode = INV_CAL;
                }
        } else if (strcmp(fileContentsType[i], "VERSION") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {//in create vcal state
            //set version
            if(cal->version != -1) {
                returnCode = DUP_VER;
            } else if (isVersionMalformed(fileContentsData[i]) == 0) {
                returnCode = INV_VER;
            } else {
                cal->version = atof(fileContentsData[i]);
            }
        } else if (strcmp(fileContentsType[i], "PRODID") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {
            if(strcmp(cal->prodID, "-1") != 0) {
                returnCode = DUP_PRODID;
            } else if (strcmp(fileContentsData[i], "") == 0 || fileContentsData == NULL) {
                returnCode = INV_PRODID;
            } else {
                strcpy(cal->prodID, fileContentsData[i]);
            }
        } else if (strcmp(fileContentsType[i], "UID") == 0 && strcmp(state[stateNum], "VEVENT") == 0) {
            //set UID
            strcpy(cal->event->UID, fileContentsData[i]);
        } else if (strcmp(fileContentsType[i], "DTSTAMP") == 0 && strcmp(state[stateNum], "VEVENT") == 0) {
            //set DTSTAMP
            if (isDateTimeMalformed(fileContentsData[i]) == 0) {
                returnCode = INV_CREATEDT;
            } else {
                char date[9];
                char time[7];
                strncpy(date, fileContentsData[i], 8);
                date[8] = '\0';
                char* p = strchr(fileContentsData[i], 'T');
                for(int i = 1; i < 7; i++) {
                    time[i-1] = p[i];
                    time[i] = '\0';
                }
                if (p[7] == 'Z') {
                    cal->event->creationDateTime.UTC = true;
                } else {
                    cal->event->creationDateTime.UTC = false;
                }
                strcpy(cal->event->creationDateTime.time, time);
                strcpy(cal->event->creationDateTime.date, date);
            }
        } else if (strcmp(fileContentsType[i], "ACTION") == 0 && strcmp(state[stateNum], "VALARM") == 0) {
            List alarmList = cal->event->alarms;
            Alarm * alarm = getFromBack(alarmList);
            strcpy(alarm->action, fileContentsData[i]);
        } else if (strcmp(fileContentsType[i], "TRIGGER") == 0 && strcmp(state[stateNum], "VALARM") == 0) {
            List alarmList = cal->event->alarms;
            Alarm * alarm = getFromBack(alarmList);
            alarm->trigger = malloc(sizeof(char) * (strlen(fileContentsData[i]) + 1));
            strcpy(alarm->trigger, fileContentsData[i]);
            isTrigger = 1;
        } else if (strcmp(state[stateNum], "VALARM") == 0) {//parsing alarm properties
            List alarmList = cal->event->alarms;
            Alarm * alarm = getFromBack(alarmList);
            Property * prop = malloc(sizeof(Property) + ((1 + strlen(fileContentsData[i])) *sizeof(char)));
            if (strcmp(fileContentsType[i], "") == 0 || fileContentsType[i] == NULL || strcmp(fileContentsData[i], "") == 0 || fileContentsData[i] == NULL) {
                returnCode = INV_EVENT;
            }
            strcpy(prop->propName, fileContentsType[i]);
            strcpy(prop->propDescr, fileContentsData[i]);
            insertBack(&alarm->properties, prop);
        } else if (strcmp(state[stateNum], "VEVENT") == 0) {//parsing event properties            
            List propList = cal->event->properties;
            Property * prop = malloc(sizeof(Property) + sizeof(char)*(1 + strlen(fileContentsData[i])));
            if (strcmp(fileContentsType[i], "") == 0 || fileContentsType[i] == NULL || strcmp(fileContentsData[i], "") == 0 || fileContentsData[i] == NULL) {
                returnCode = INV_EVENT;
            }
            strcpy(prop->propName, fileContentsType[i]);
            strcpy(prop->propDescr, fileContentsData[i]);
            insertBack(&propList, prop);
            cal->event->properties = propList;
        }
    }
    
    if (returnCode != OK) {
        deleteCalendar(cal);
    } else {
        *obj = cal;
    }
    
    for (int i = 0; i < fileLenght; i++) {
        free(fileContentsType[i]);
        free(fileContentsData[i]);
    }
    free(fileContentsType);
    free(fileContentsData);
    free(state);    

    return returnCode;
}


/** Function to delete all calendar content and free all the memory.
 *@pre Calendar object exists, is not null, and has not been freed
 *@post Calendar object had been freed
 *@return none
 *@param obj - a pointer to a Calendar struct
**/

void deleteCalendar(Calendar* obj) {

    if (obj->event->alarms.head != NULL) {
        Alarm* elem;
        ListIterator iter = createIterator(obj->event->alarms);

        while ((elem = nextElement(&iter)) != NULL) {
            clearList(&elem->properties);
        }
    }
    clearList(&obj->event->alarms);
    clearList(&obj->event->properties);
    free(obj->event);
    free(obj);
}



/** Function to create a string representation of a Calendar object.
 *@pre Calendar object exists, is not null, and is valid
 *@post Calendar has not been modified in any way, and a string representing the Calndar contents has been created
 *@return a string contaning a humanly readable representation of a Calendar object
 *@param obj - a pointer to a Calendar struct
**/

char* printCalendar(const Calendar* obj) {
    char* printStr;
    char* tmpStr;
        
    if (obj == NULL) {
        return "list is null\n";
    }
    
    tmpStr = (char*)malloc(sizeof(char)*1000);
    printStr = (char*)malloc(sizeof(char)*10000);

    sprintf(tmpStr, "Calendar: version = %f, prodID = %s\n", obj->version, obj->prodID);
    strcat(printStr, tmpStr);
    sprintf(tmpStr, "Event\n\tUID = %s\n", obj->event->UID);
    strcat(printStr, tmpStr);
    int UTC = 0;
    if (obj->event->creationDateTime.UTC) {
        UTC = 1;
    }
    sprintf(tmpStr, "\tcreationDateTime = %s:%s, UTC=%d\n", obj->event->creationDateTime.date, obj->event->creationDateTime.time, UTC);
    strcat(printStr, tmpStr);
    //alarm
    sprintf(tmpStr, "\tAlarms:\n");
    strcat(printStr, tmpStr);

    if (obj->event->alarms.head != NULL) {    
        Alarm* elemA;
        ListIterator iterA = createIterator(obj->event->alarms);
    
        while ((elemA = nextElement(&iterA)) != NULL) {
            Alarm * alarm = elemA;
            sprintf(tmpStr, "\t\tAction: %s\n\t\tTrigger: %s\n", alarm->action, alarm->trigger);
            strcat(printStr, tmpStr);
            //alarm properties
            sprintf(tmpStr, "\t\tProperties:\n");
            strcat(printStr, tmpStr);

            if (alarm->properties.head != NULL) {
                Property* elem;
                ListIterator iter = createIterator(alarm->properties);

                while ((elem = nextElement(&iter)) != NULL) {
                    Property * prop = elem;
                    sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
                    strcat(printStr, tmpStr);
                }
                sprintf(tmpStr, "\n");
                strcat(printStr, tmpStr);
            }
        }
    }
    //event properties
    sprintf(tmpStr, "\n\tOther properties:\n");
    strcat(printStr, tmpStr);

    if (obj->event->properties.head != NULL) {
        Property* elem;
        ListIterator iter = createIterator(obj->event->properties);

        while ((elem = nextElement(&iter)) != NULL) {
            Property * prop = elem;
            sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
            strcat(printStr, tmpStr);
        }
    }
    free(tmpStr);
    return printStr;
}

char* printError(ErrorCode err) {
    if (err == OK) {
        return "OK";
    } else if (err == INV_FILE) {
        return "INV_FILE";
    } else if (err == INV_CAL) {
        return "INV_CAL";
    } else if (err == INV_VER) {
        return "INV_VER";
    } else if (err == INV_PRODID) {
        return "INV_PRODID";
    } else if (err == DUP_VER) {
        return "DUP_VER";
    } else if (err == DUP_PRODID) {
        return "DUP_PRODID";
    } else if (err == INV_EVENT) {
        return "INV_EVENT";
    } else if (err == INV_CREATEDT) {
        return "INV_CREATEDT";
    } else if (err == OTHER_ERROR) {
        return "OTHER_ERROR";
    }
    return "OTHER_ERROR";
}
