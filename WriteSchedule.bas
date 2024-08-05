Option Explicit

' Outlook VBA that extracts Outlook Calendar items and writes them to file
' ("C:\Coding\PyCharm\projects\OnlineCalendar\templates\schedule.tsv"). 

Private Function MinDate(dtDate1 As Date, dtDate2 As Date) As Date
    ' Return the earlier of two dates.
    If dtDate1 < dtDate2 Then
        MinDate = dtDate1
    Else
        MinDate = dtDate2
    End If
End Function

Private Function MaxDate(dtDate1 As Date, dtDate2 As Date) As Date
    ' Return the later of two dates.
    If dtDate1 > dtDate2 Then
        MaxDate = dtDate1
    Else
        MaxDate = dtDate2
    End If
End Function

Private Function GetCalendarObject(ParentFolder As String, SubFolder As String) As Outlook.Folder

    ' Outlook folders.
    Dim oFolder As Outlook.Folder
    Dim oSubFolder As Outlook.Folder
    Dim oCalendar As Outlook.Folder
    Dim FolderPath As String
    
    FolderPath = "\\" & ParentFolder & "\" & SubFolder
    
    ' Loop over all top-level folders.
    For Each oFolder In Application.Session.Folders
        If oFolder.Name = ParentFolder Then
            ' Loop over subfolders.
            For Each oSubFolder In oFolder.Folders
                If oSubFolder.Name = SubFolder And oSubFolder.DefaultItemType = olAppointmentItem Then
                    ' Calendar folders only.
                    If oSubFolder.FolderPath = FolderPath Then
                        ' Get object whose folder path is the desired folder path.
                        Set GetCalendarObject = oSubFolder
                        Exit For
                    End If
                End If
            Next
        End If
    Next
    
    If GetCalendarObject Is Nothing Then
        MsgBox "Failed to find object for folder path " + FolderPath
    End If

End Function

' For publishing my calendar to davidtutor.neocities.org.
' Important constraint.  There cannot be two "Busy" calendar items with overlapping times.
Public Sub WriteSchedule()

    Dim num_days As Integer
    num_days = 10

    Dim output_file As String
    output_file = "C:\Coding\PyCharm\projects\OnlineCalendar\templates\schedule.tsv"

    ' Get Outlook appointments.
    Dim oItems As Outlook.Items
    Dim oItemsForExport As Outlook.Items
    Dim oItem As Outlook.AppointmentItem
    Dim oShell As Object

    ' Select appointments for each day in the next 10 days.
    Dim dtToday As Date
    'Dim dtDayStartTime As Date
    Dim dtRangeStart As Date
    Dim dtRangeEnd As Date
    Dim strRestriction As String

    ' My usual working hours.
    'Dim dtNormalDayStartTime As Date

    ' Appointment start and end times.
    Dim dtItemStartTime As Date
    Dim dtItemEndTime As Date

    ' For working with files.
    Dim fso As Object
    Dim oFile As Object

    ' Date/Time format
    Dim dtFormat As String

    Dim WshShell

    ' Initialize Globals and Constants
    'dtNormalDayStartTime = 9 / 24 ' 9:00am
    dtFormat = "yyyy/mm/dd hh:mm:ss"

    Set oItems = GetCalendarObject("iCloud", "Calendar").Items
    oItems.IncludeRecurrences = True
    oItems.Sort "[Start]"

    ' Define date/time range to get.
    'dtDayStartTime = MaxDate(dtNormalDayStartTime, Hour(Now) / 24)
    dtToday = Int(Date)
    'dtRangeStart = dtToday + dtDayStartTime
    dtRangeStart = dtToday + Hour(Now) / 24
    dtRangeEnd = dtToday + num_days - (1 / 60 / 24) ' 11:59pm

    strRestriction = "[Start] <= '" & Format$(dtRangeEnd, "mm/dd/yyyy hh:mm AMPM") & _
    "' AND [End] >= '" & Format$(dtRangeStart, "mm/dd/yyyy hh:mm AMPM") & _
    "' AND [BusyStatus] = " & CStr(olBusy)


    Set oItemsForExport = oItems.Restrict(strRestriction)

    ' Open File for Export.
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set oFile = fso.CreateTextFile(output_file)
    ' Debug.Print Format$(dtRangeStart, "mm/dd/yyyy hh:mm AMPM"), Format$(dtRangeEnd, "mm/dd/yyyy hh:mm AMPM")

    For Each oItem In oItemsForExport
        ' Get appointment's start date/time.
        dtItemStartTime = oItem.Start - Int(oItem.Start)
        ' Get appointment's end date/time.
        dtItemEndTime = oItem.End - Int(oItem.End)
        If InStr(1, oItem.Categories, "Busy", 1) > 0 Then
            oFile.WriteLine Format$(oItem.Start, dtFormat) & vbTab & Format$(oItem.End, dtFormat)
            ' Debug.Print Format$(oItem.Start, dtFormat) & vbTab & Format$(oItem.End, dtFormat)
        End If
    Next oItem
    
    ' Add date/time VBA executed to end of file.
    oFile.WriteLine "Written" & vbTab & Format$(DateTime.Now, dtFormat)

    ' Close File
    oFile.Close
    Set fso = Nothing
    Set oFile = Nothing

    Set WshShell = CreateObject("WScript.Shell")

    WshShell.Run """C:\ProgramData\Microsoft\Windows\Start Menu\Programs\CalendarUpdate.bat.lnk"""

    Set oShell = CreateObject("WScript.Shell")
    oShell.Run "mshta.exe vbscript:close(CreateObject(""WScript.shell"").Popup(""All Done""," & 2 & ",""Microsoft Outlook VBA""))"

End Sub
