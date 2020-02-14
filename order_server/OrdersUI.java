/******************************************************************************************************************
* File:OrdersUI.java
* Course: Project Course
* Project: Fullfillment Center
* Copyright: Copyright (c) 2018 Carnegie Mellon University
* Versions:
*   1.0 April 2018 - Initial write of course order server demo (Lattanze).
*   2.0 November 2019 - Adapted for IITP project course. Changed database and order submission URL.
*
* Description: This class is the console for the an orders database. This interface uses a webservices client class
* to update the orderinfo MySQL database. 
*
* Parameters: None
*
* Internal Methods: 
*  String GetOrderCount ( String product ) - Returns the order count to the number of products ordered ensuring that 
*                                            the user input is correct and in bounds.
*  static void ParseAndPrint ( String ReturnQuery )-  Parses the return query and prints the records if there are 
*													  any.
*
* External Dependencies (one of the following):
*	- WSClientAPI - this class provides a restful interface to a node.js webserver (see Server.js and REST.js).
*
******************************************************************************************************************/

import java.util.Scanner;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.io.Console;

public class OrdersUI
{
	public static void main(String args[])
	{
		boolean done = false;						// main loop flag
		boolean error = false;						// error flag
		char    option;								// Menu choice from user
		Console c = System.console();				// Console string input
		Scanner keyboard = new Scanner(System.in);	// Console integer input

		String  customer = null;					// order date
		String 	response = null;					// response string from REST 
		String  orderid = null;						// Order ID
		String  red = null;							// red square count
		String  blue = null;						// blue square count
		String  green = null;						// green square count
		String  custaddress = null;					// customer address
	
		DateTimeFormatter dtf = null;				// Date object formatter
		LocalDate localDate = null;					// Date object
		WSClientAPI api = new WSClientAPI();		// RESTful api object

		/////////////////////////////////////////////////////////////////////////////////
		// Main UI loop
		/////////////////////////////////////////////////////////////////////////////////

		while (!done)
		{	
			// Here, is the main menu set of choices

			System.out.println( "\n\n\n\nPending Orders Operations:" );
			System.out.println( "===============================================" );
			System.out.println( "Select an Option: \n" );
			System.out.println( "1: List all pending orders." );
			System.out.println( "2: Retrieve a pending order by ID." );
			System.out.println( "3: Retrieve a customer's pending orders." );
			System.out.println( "4: Add a new order to the order database." );
			System.out.println( "5: Mark an order (by id) as fulfilled.");
			System.out.println( "6: List all filled orders." );
			System.out.println( "7: Retrieve a customer's filled orders." );
			System.out.println( "8: Delete an order by ID." );							
			System.out.println( "X: Exit\n" );
			System.out.print( "\n>>>> " );
			option = keyboard.next().charAt(0);	
			keyboard.nextLine();	// Removes data from keyboard buffer. If you don't clear the buffer, you blow 
									// through the next call to nextLine()

			//////////// option 1 - retrieve all the orders in the order database ////////////

			if ( option == '1' )
			{


				System.out.println( "\nRetrieving All PENDING Orders::" );
				try
				{
					response = api.retrievePendingOrders();

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);

				}

				if (!ErrorQueryStatus(response))
				{
					ParseAndPrint(response);
				} else {
					System.out.print("Error retrieving pending orders. ");
				}			

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option 2 - retrieve a pending order by ID ////////////

			if ( option == '2' )
			{
				// Here we get the order ID from the user

				error = true;

				while (error)
				{
					System.out.print( "\nEnter the order ID: " );
					orderid = keyboard.nextLine();

					try
					{
						Integer.parseInt(orderid);
						error = false;
					} catch (NumberFormatException e) {

						System.out.println( "Not a number, please try again..." );
						System.out.println("\nPress enter to continue..." );

					} // if

				} // while

				try
				{
					response = api.retrievePendingOrders(Integer.parseInt(orderid));

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);
					
				}

				if (!ErrorQueryStatus(response))
				{
					ParseAndPrint(response);
				} else {
					System.out.print("Error retrieving pending order. ");
				}				

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option 3 ////////////

			if ( option == '3' )
			{
				// Here we get the customer name from the user

				System.out.print( "\nEnter the customer name: " );
				customer = keyboard.nextLine();

				try
				{
					response = api.retrievePendingOrders(customer);

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);
					
				}

				if (!ErrorQueryStatus(response))
				{
					ParseAndPrint(response);
				}else {
					System.out.print("Error retrieving customer's pending orders. ");
				}	

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option 4 - Add a new order to the order database ////////////

			if ( option == '4' )
			{
				// Here we create a new order entry in the database

				//dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd");
				//localDate = LocalDate.now();
				//date = localDate.format(dtf);

				System.out.println("Customer name:");
				customer = keyboard.nextLine();

				System.out.println("Customer address:");
				custaddress = keyboard.nextLine();

				System.out.println("Enter the quantity of each product::");				
				System.out.println("====================================\n");
				
				// Square products.

				red 	= GetOrderCount( "red squares" );
				blue 	= GetOrderCount( "blue squares" );
				green	= GetOrderCount( "green squares" );

				System.out.println("Creating the following order:");
				System.out.println("==============================");
				System.out.println(" Customer name:" 	+ customer);
				System.out.println(" red square(s):" 	+ red);
				System.out.println(" blue square(s)" 	+ blue);
				System.out.println(" green square(s):" 	+ green);
				System.out.println("==============================");					
				System.out.println("\nPress 'y' to create this order:");

				option = keyboard.next().charAt(0);

				if (( option == 'y') || (option == 'Y'))
				{
					try
					{
						System.out.println("\nCreating order...");
						response = api.newOrder(customer, red, blue, green, custaddress);

					} catch(Exception e) {

						System.out.println("Request failed:: " + e);
					}

				} else {

					System.out.println("\nOrder not created...");
				}

				if (!ErrorQueryStatus(response))
				{
					System.out.print("Order created successfully! ");
				} else {
					System.out.print("Error adding order. ");
				}

				System.out.println("Press enter to continue..." );
				c.readLine();

				option = ' '; //Clearing option. This in case the user enterd X/x the program will not exit.

			} // if

			//////////// option 5 - mark an order as fulfilled ////////////

			if ( option == '5' )
			{
				// Here we get the order ID from the user

				error = true;

				while (error)
				{
					System.out.print( "\nEnter the order ID to mark as fulfilled: " );
					orderid = keyboard.nextLine();

					try
					{
						Integer.parseInt(orderid);
						error = false;
					} catch (NumberFormatException e) {

						System.out.println( "Not a number, please try again..." );
						System.out.println("\nPress enter to continue..." );

					} // if

				} // while

				try
				{
					response = api.markOrderFilled(Integer.parseInt(orderid));

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);
					
				}

				if (!ErrorQueryStatus(response))
				{
					System.out.print("Order successfully marked as fulfilled! ");
				} else {
					System.out.print("Error marking order as fulfilled. ");
				}

				System.out.println("Press enter to continue..." );
				c.readLine();

			} // if


			//////////// option 6 - retrieve all filled orders ////////////			

			if ( option == '6' )
			{
				System.out.println( "\nRetrieving All FULFILLED Orders::" );
				try
				{
					response = api.retrieveFilledOrders();

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);

				}

				if (!ErrorQueryStatus(response))
				{
					ParseAndPrint(response);
				} else {
					System.out.print("Error retrieving fulfilled orders. ");
				}			

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option 7 - retrieve a customer's filled orders ////////////

			if ( option == '7' )
			{
				// Here we get the customer name from the user

				System.out.print( "\nEnter the customer name: " );
				customer = keyboard.nextLine();

				try
				{
					response = api.retrieveFilledOrders(customer);

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);
					
				}

				if (!ErrorQueryStatus(response))
				{
					ParseAndPrint(response);
				} else {
					System.out.print("Error customer's fulfilled orders. ");
				}			

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option 8 - delete order by ID ////////////			

			if ( option == '8' )
			{
				// Here we get the order ID from the user

				error = true;

				while (error)
				{
					System.out.print( "\nEnter the order ID to delete: " );
					orderid = keyboard.nextLine();

					try
					{
						Integer.parseInt(orderid);
						error = false;
					} catch (NumberFormatException e) {

						System.out.println( "Not a number, please try again..." );
						System.out.println("\nPress enter to continue..." );

					} // if

				} // while

				try
				{
					response = api.deleteOrder(Integer.parseInt(orderid));

				} catch (Exception e) {

					System.out.println("Request failed:: " + e);
					
				}

				if (!ErrorQueryStatus(response))
				{
					System.out.print("Order deleted successfully. ");
				} else {
					System.out.print("Problem deleting order. ");
				}

				System.out.println("\nPress enter to continue..." );
				c.readLine();

			} // if

			//////////// option X - exit the program ////////////

			if ( ( option == 'X' ) || ( option == 'x' ))
			{
				// Here the user is done, so we set the Done flag and halt the system

				done = true;
				System.out.println( "\nDone...\n\n" );

			} // if

		} // while

  	} // main


  	//////////////////////////////////////////////////////////////////////////////////
	// This method returns the number of products ordered ensuring that the user input
	// is correct an in bounds.
	//////////////////////////////////////////////////////////////////////////////////

  	private static String GetOrderCount ( String product )
  	{			
		boolean done=false;						    // loop flag
		boolean error=true;							// error flag
		Scanner in = new Scanner(System.in);		// Console integer input
		Integer ordercount=0;						// Number of items

		while( !done )
		{
       		System.out.print("How many " + product + " products >> ");

        	if (in.hasNextInt()) 
        	{
        		ordercount = in.nextInt();
       			error = false;
       			done = true;

       		} else {

        		System.out.println("Must enter positive integers...");
            	in.next();
            	System.out.println();
            	error = true;

            } // if
        } // while

		if (!error)
			if (ordercount < 0 )
			{
				System.out.println( "Product quantities must be positive...");
			} else  {
				System.out.println("OK you specified " + ordercount + " " + product + " products.");
				done = true;
			} // if

		return(ordercount.toString());

	} // GetOrderCount

	//////////////////////////////////////////////////////////////////////////////////
	// Returns the error code from the return query string.
	//////////////////////////////////////////////////////////////////////////////////

	private static boolean ErrorQueryStatus ( String ReturnQuery )
	{
		int lefttoken = ReturnQuery.indexOf(":");
		int righttoken = ReturnQuery.indexOf(",");		

		String status = ReturnQuery.substring(lefttoken + 1, righttoken);

		return( status.equalsIgnoreCase("true") );

	}

	//////////////////////////////////////////////////////////////////////////////////
	// Parses the return query and prints the records if there are any.
	//////////////////////////////////////////////////////////////////////////////////

	private static void ParseAndPrint ( String ReturnQuery )
	{
		int 	begintoken = ReturnQuery.indexOf("[");
		int 	endtoken = ReturnQuery.indexOf("]");		
		int 	lefttoken;
		int 	righttoken;
		int 	beginfield;
		int     endfield;
		int 	cnt;
		String 	record;
		boolean	done, endrecord;

		if (begintoken+1 == endtoken)
		{
			System.out.println("\nThere are no matching records...");

		} else {

			// in this loop we parse out each record

			done = false;
			cnt=1;
			while (!done)
			{	
				// find next record, note records are bound by {}
				lefttoken = ReturnQuery.indexOf("{", begintoken);
				righttoken = ReturnQuery.indexOf("}", begintoken);

				// here we get rid of all the " marks
				record = ReturnQuery.substring(lefttoken+1, righttoken);
				record = record.replace("\"", "");

				// here we start parsing the individual record and print it.
				endrecord = false;
				beginfield = 0;
				endfield = record.indexOf(",", beginfield);
				System.out.println("Record " + record.substring(beginfield, endfield));
				System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");

				while(!endrecord)
				{
					beginfield = endfield + 1;
					endfield = record.indexOf(",", beginfield);

					if (endfield != -1)
					{
						System.out.println(">> "+record.substring(beginfield, endfield));
					} else {
						System.out.println(">> "+record.substring(beginfield, record.length()-1));							
						endrecord = true;
					}
				}

				// here we check to see if we are don processing records				
			
				if (ReturnQuery.indexOf("]", begintoken) == righttoken+1)
				{
					done = true;
				} else {
					begintoken = righttoken + 1;
					cnt++;
					System.out.println();
				}
			}

			System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
			System.out.println("Done:: " + cnt + " records found.");
		}
	}

} // OrdersUI
