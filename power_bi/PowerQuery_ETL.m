// ===============================================================================
// POWER QUERY (M) ETL SCRIPT SPECIFICATION FOR MYSQL 8.4 INTEGRATION
// Copy and Paste into Power BI Desktop "Advanced Editor" for Table Transformations
// Source Database: MySQL 8.4 (hotel_analytics_db on localhost:3306)
// ANALYTICAL PERIOD: January 1, 2025 - June 30, 2026
// ===============================================================================

// -------------------------------------------------------------------------------
// 1. DimDate (Dynamic Calendar Table Generator for Jan 2025 - Jun 2026)
// -------------------------------------------------------------------------------
let
    StartDate = #date(2025, 1, 1),
    EndDate = #date(2026, 6, 30),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    SourceDates = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(SourceDates, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    SetTypeDate = Table.TransformColumnTypes(TableFromList, {{"Date", type date}}),
    
    // Add Calendar Columns
    AddYear = Table.AddColumn(SetTypeDate, "Year", each Date.Year([Date]), Int64.Type),
    AddMonthNo = Table.AddColumn(AddYear, "Month Number", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonthNo, "Month Name", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddYearMonth = Table.AddColumn(AddQuarter, "Year-Month", each Text.From(Date.Year([Date])) & "-" & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"), type text),
    AddDayNo = Table.AddColumn(AddYearMonth, "Day", each Date.Day([Date]), Int64.Type),
    AddDayName = Table.AddColumn(AddDayNo, "Day Name", each Date.DayOfWeekName([Date]), type text),
    AddWeekNo = Table.AddColumn(AddDayName, "Week Number", each Date.WeekOfYear([Date]), Int64.Type),
    AddIsWeekend = Table.AddColumn(AddWeekNo, "IsWeekend", each if Date.DayOfWeek([Date]) >= 5 then "Weekend" else "Weekday", type text)
in
    AddIsWeekend

// -------------------------------------------------------------------------------
// 2. FactBookings Transformation Query
// -------------------------------------------------------------------------------
/*
let
    Source = MySQL.Database("localhost:3306", "hotel_analytics_db", [Query="SELECT * FROM bookings WHERE check_in_date <= '2026-06-30'"]),
    SetTypes = Table.TransformColumnTypes(Source,{
        {"id", Int64.Type},
        {"booking_reference", type text},
        {"guest_id", Int64.Type},
        {"room_id", Int64.Type},
        {"check_in_date", type date},
        {"check_out_date", type date},
        {"num_guests", Int64.Type},
        {"status", type text},
        {"total_amount", Currency.Type},
        {"payment_status", type text},
        {"created_at", type datetime}
    }),
    
    // Add Calculated Columns
    AddNightsStayed = Table.AddColumn(SetTypes, "nights_stayed", each Duration.Days([check_out_date] - [check_in_date]), Int64.Type),
    AddLeadTimeDays = Table.AddColumn(AddNightsStayed, "lead_time_days", each Duration.Days([check_in_date] - Date.From([created_at])), Int64.Type)
in
    AddLeadTimeDays
*/
