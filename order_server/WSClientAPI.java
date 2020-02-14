/******************************************************************************************************************
* File:WSClientAPI.java
* Course: Project Course
* Project: Fullfillment Center
* Copyright: Copyright (c) 2018 Carnegie Mellon University
* Versions:
*   1.0 April 2018 - Initial write of course order server demo (Lattanze).
*   2.0 November 2019 - Adapted for IITP project course. Changed database and order submission URL.
*
* Description: This class is used to provide access to a Node.js server. The server for this application is 
* Server.js which provides RESTful services to access a MySQL database.
*
* Parameters: None
*
* Internal Methods: None
*  String retrievePendingOrders() - gets and returns all the orders in the orderinfo database
*  String retrievePendingOrders(Integer id) - gets and returns the order associated with the order id
*  String retrievePendingOrders(String Customer) - gets and returns the order associated with the customer name
*  String retrieveFilledOrders() - gets and returns all the fulfilled orders in the database
*  String retrieveFilledOrders(String Customer) - gets and returns all the fulfilled orders in the database 
*                                                 assocated with customer name
*  String newOrder(String customer, String red, String blue, String green, String custaddress) - creates a new 
*  order in the orderinfo database
*  String markOrderFilled(Integer id) - marks order id as fulfilled
*  String deleteOrder(Integer id) - deletes order id from the database
*
* External Dependencies: None
******************************************************************************************************************/

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.nio.charset.StandardCharsets;

public class WSClientAPI
{
	/********************************************************************************
	* Description: Gets and returns all the pending orders in the orderinfo database
	* Parameters: None
	* Returns: String of all the current orders in the orderinfo database
	********************************************************************************/

	public String retrievePendingOrders() throws Exception
	{
		// Set up the URL and connect to the node server

		String url = "http://localhost:3000/api/pending";

		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("GET");
		int responseCode = con.getResponseCode();


		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.
		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}
	
	/********************************************************************************
	* Description: Gets and returns the pending orders based on the provided id
	*              from the orderinfo database.
	* Parameters: None
	* Returns: String of all the order corresponding to the id argument in the 
	*		   orderinfo database.
	********************************************************************************/

	public String retrievePendingOrders(Integer id) throws Exception
	{
		// Set up the URL and connect to the node server
		String url = "http://localhost:3000/api/pending/"+id.toString();
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("GET");
		int responseCode = con.getResponseCode();

		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}

	/********************************************************************************
	* Description: Gets and returns all the pending orders for a customer name.
	* Parameters: None
	* Returns: String of all the order corresponding to the id argument in the 
	*		   orderinfo database.
	********************************************************************************/

	public String retrievePendingOrders(String customer) throws Exception
	{
		// Set up the URL and connect to the node server
		String url = "http://localhost:3000/api/pendingcustorders/"+customer;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("GET");
		int responseCode = con.getResponseCode();

		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}

	/********************************************************************************
	* Description: Gets and returns all the fulfilled orders in the orderinfo
	* database.
	* Parameters: None
	* Returns: String of all the current orders in the orderinfo database
	********************************************************************************/

	public String retrieveFilledOrders() throws Exception
	{
		// Set up the URL and connect to the node server

		String url = "http://localhost:3000/api/filled";

		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("GET");
		int responseCode = con.getResponseCode();


		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.
		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}

	/********************************************************************************
	* Description: Gets and returns all the filled orders for a customer name.
	* Parameters: None
	* Returns: String of all the order corresponding to the id argument in the 
	*		   orderinfo database.
	********************************************************************************/

	public String retrieveFilledOrders(String customer) throws Exception
	{
		// Set up the URL and connect to the node server
		String url = "http://localhost:3000/api/filledcustorders/"+customer;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("GET");
		int responseCode = con.getResponseCode();

		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}


	/********************************************************************************
	* Description: Posts a new order to the orderinfo database
	* Parameters: None
	* Returns: String that contains the status of the POST operation
	********************************************************************************/

   	public String newOrder(String customer, String red, String blue, String green, String custaddress) throws Exception
	{
		// Set up the URL and connect to the node server		
		URL url = new URL("http://localhost:3000/api/neworder");
		HttpURLConnection conn = (HttpURLConnection) url.openConnection();

		// The POST parameters
		String input = "&customer="+customer+"&red="+red+"&blue="+blue+"&green="+green+"&address="+custaddress;

		//Configure the POST connection for the parameters
		conn.setRequestMethod("POST");
        conn.setRequestProperty("Accept-Language", "en-GB,en;q=0.5");
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        conn.setRequestProperty("Content-length", Integer.toString(input.length()));
        conn.setRequestProperty("Content-Language", "en-GB");
        conn.setRequestProperty("charset", "utf-8");
        conn.setUseCaches(false);
        conn.setDoOutput(true);

        // Set up a stream and write the parameters to the server
		OutputStream os = conn.getOutputStream();
		os.write(input.getBytes());
		os.flush();

		//Loop through the input and build the response string.
		//When done, close the stream.	
		BufferedReader in = new BufferedReader(new InputStreamReader((conn.getInputStream())));
		String inputLine;		
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		
		in.close();
		conn.disconnect();

		return(response.toString());
		
    } // newOrder

	/********************************************************************************
	* Description: Marks an order as fulfilled
	* Parameters: None
	* Returns: String that contains the status of the POST operation
	********************************************************************************/

    public String markOrderFilled(Integer id) throws Exception
	{
		// Set up the URL and connect to the node server
		String url = "http://localhost:3000/api/markOrderFilled/"+id.toString();
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("POST");
		int responseCode = con.getResponseCode();

		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}

	/********************************************************************************
	* Description: Dete an order from the orderinfo database.
	* Parameters: None
	* Returns: Status of delete operation.
	********************************************************************************/

	public String deleteOrder(Integer id) throws Exception
	{
		// Set up the URL and connect to the node server
		String url = "http://localhost:3000/api/deleteOrder/"+id.toString();
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//Form the request header and instantiate the response code
		con.setRequestMethod("DELETE");
		int responseCode = con.getResponseCode();

		//Set up a buffer to read the response from the server
		BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		//Loop through the input and build the response string.
		//When done, close the stream.		

		while ((inputLine = in.readLine()) != null) 
		{
			response.append(inputLine);
		}
		in.close();

		return(response.toString());

	}

} // WSClientAPI