import requests
import urllib3

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)  # disable ssl warning


class REST:
    """Allows to send REST API requests to Interactive Brokers Client Portal Web API.

    :param url: Gateway session link, defaults to "https://localhost:5000"
    :type url: str, optional
    :param ssl: Usage of SSL certificate, defaults to False
    :type ssl: bool, optional
    """

    def __init__(self, url="https://localhost:5000", ssl=False) -> None:
        """Create a new instance to interact with REST API

        :param url: Gateway session link, defaults to "https://localhost:5000"
        :type url: str, optional
        :param ssl: Usage of SSL certificate, defaults to False
        :type ssl: bool, optional
        """
        self.url = f"{url}/v1/api/"
        self.ssl = ssl
        self.id = self.get_accounts()[0]["accountId"]

    def validate_sso_session(self):
        endpoint = "sso/validate"
        headers = {'Accept': 'application/json'}
        try:
            response = requests.get(self.url + endpoint, headers=headers)
            if response.status_code == 200:
                result = response.json()
                # Process the response data as needed
                return result
            else:
                print(f"Request failed with status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {str(e)}")

        return None

    def get_accounts(self) -> list:
        """Returns account info

        :return: list of account info
        :rtype: list
        """
        response = requests.get(f"{self.url}portfolio/accounts", verify=self.ssl)
        return response.json()

    def switch_account(self, accountId: str) -> dict:
        """Switch selected account to the input account

        :param accountId: account ID of the desired account
        :type accountId: str
        :return: Response from the server
        :rtype: dict
        """
        response = requests.post(
            f"{self.url}iserver/account", json={"acctId": accountId}, verify=self.ssl
        )

        self.id = accountId
        return response.json()

    def get_cash(self) -> float:
        """Returns cash balance of the selected account

        :return: cash balance
        :rtype: float
        """
        response = requests.get(
            f"{self.url}portfolio/{self.id}/ledger", verify=self.ssl
        )

        return response.json()["USD"]["cashbalance"]

    def get_netvalue(self) -> float:
        """Returns net value of the selected account

        :return: Net value in USD
        :rtype: float
        """
        response = requests.get(
            f"{self.url}portfolio/{self.id}/ledger", verify=self.ssl
        )

        return response.json()["USD"]["netliquidationvalue"]

    def get_conid(
        self,
        symbol: str,
        instrument_filters: dict = None,
        contract_filters: dict = {"isUS": True},
    ) -> int:
        """Returns contract id of the given stock instrument

        :param symbol: Symbol of the stock instrument
        :type symbol: str
        :param instrument_filters: Key-value pair of filters to use on the returned instrument data, e.g) {"name": "ISHARES NATIONAL MUNI BOND E", "assetClass": "STK"}
        :type instrument_filters: Dict, optional
        :param contract_filters: Key-value pair of filters to use on the returned contract data, e.g) {"isUS": True, "exchange": "ARCA"}
        :type contract_filters: Dict, optional
        :return: contract id
        :rtype: int
        """
        query = {"symbols": symbol}
        response = requests.get(
            f"{self.url}trsrv/stocks", params=query, verify=self.ssl
        )

        dic = response.json()

        if instrument_filters or contract_filters:

            def filter_instrument(instrument: dict) -> bool:
                def apply_filters(x: dict, filters: dict) -> list:
                    positives = list(
                        filter(
                            lambda x: x,
                            [x.get(key) == val for key, val in filters.items()],
                        )
                    )
                    return len(positives) == len(filters)

                if instrument_filters:
                    valid = apply_filters(instrument, instrument_filters)

                    if not valid:
                        return False

                if contract_filters:
                    instrument["contracts"] = list(
                        filter(
                            lambda x: apply_filters(x, contract_filters),
                            instrument["contracts"],
                        )
                    )

                return len(instrument["contracts"]) > 0

            dic[symbol] = list(filter(filter_instrument, dic[symbol]))

        return dic[symbol][0]["contracts"][0]["conid"]

    def get_portfolio(self) -> dict:
        """Returns portfolio of the selected account

        :return: Portfolio
        :rtype: dict
        """
        response = requests.get(
            f"{self.url}portfolio/{self.id}/positions/0", verify=self.ssl
        )

        dic = {item["contractDesc"]: item["position"] for item in response.json()}
        dic["USD"] = self.get_cash()
        return dic

    def get_portfolio_accounts(self) -> list:
        """Returns a list of portfolio accounts

        :return: List of portfolio accounts
        :rtype: list
        """
        response = requests.get(f"{self.url}portfolio/accounts", verify=self.ssl)
        return response.json()

    def get_portfolio_subaccounts(self) -> list:
        """Returns a list of portfolio sub-accounts

        :return: List of portfolio sub-accounts
        :rtype: list
        """
        response = requests.get(f"{self.url}portfolio/subaccounts", verify=self.ssl)
        return response.json()

    def get_account_info(self, accountId: str) -> dict:
        """Returns account information for the specified account ID

        :param accountId: Account ID
        :type accountId: str
        :return: Account information
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/meta", verify=self.ssl)
        return response.json()

    def get_account_summary(self, accountId: str) -> dict:
        """Returns account summary for the specified account ID

        :param accountId: Account ID
        :type accountId: str
        :return: Account summary
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/summary", verify=self.ssl)
        return response.json()

    def get_account_ledger(self, accountId: str) -> dict:
        """Returns account ledger for the specified account ID

        :param accountId: Account ID
        :type accountId: str
        :return: Account ledger
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/ledger", verify=self.ssl)
        return response.json()

    def get_brokerage_accounts(self) -> dict:
        """Returns a list of brokerage accounts

        :return: Brokerage account information
        :rtype: dict
        """
        response = requests.get(f"{self.url}iserver/accounts", verify=self.ssl)
        return response.json()

    def switch_account(self, accountId: str) -> dict:
        """Switches the currently selected account to the specified account ID

        :param accountId: Account ID
        :type accountId: str
        :return: Response with updated account ID
        :rtype: dict
        """
        data = {
            "acctId": accountId
        }
        response = requests.post(f"{self.url}iserver/account", json=data, verify=self.ssl)
        return response.json()

    def get_account_pnl(self) -> dict:
        """Returns the PnL for the selected account

        :return: Account PnL
        :rtype: dict
        """
        response = requests.get(f"{self.url}iserver/account/pnl/partitioned", verify=self.ssl)
        return response.json()

    def get_account_allocation(self, accountId: str) -> dict:
        """Returns account allocation for the specified account ID

        :param accountId: Account ID
        :type accountId: str
        :return: Account allocation
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/allocation", verify=self.ssl)
        return response.json()

    def get_all_accounts_allocation(self, accountIds: list) -> dict:
        """Returns consolidated account allocation for all specified account IDs

        :param accountIds: List of account IDs
        :type accountIds: list
        :return: Consolidated account allocation
        :rtype: dict
        """
        data = {
            "acctIds": accountIds
        }
        response = requests.post(f"{self.url}portfolio/allocation", json=data, verify=self.ssl)
        return response.json()

    def get_portfolio_positions(self, accountId: str, pageId: str) -> dict:
        """Returns a list of positions for the specified account ID and page ID

        :param accountId: Account ID
        :type accountId: str
        :param pageId: Page ID
        :type pageId: str
        :return: List of positions
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/positions/{pageId}", verify=self.ssl)
        return response.json()

    def get_position_by_conid(self, accountId: str, conid: int) -> dict:
        """Returns a list of positions matching the specified contract ID (conid) for the given account ID

        :param accountId: Account ID
        :type accountId: str
        :param conid: Contract ID
        :type conid: int
        :return: List of positions
        :rtype: dict
        """
        response = requests.get(f"{self.url}portfolio/{accountId}/position/{conid}", verify=self.ssl)
        return response.json()

    def get_account_trades(self) -> list:
        """Returns a list of trades for the currently selected account

        :return: List of trades
        :rtype: list
        """
        response = requests.get(f"{self.url}iserver/account/trades", verify=self.ssl)
        return response.json()

    def preview_orders(self, account_id: str, order_info: dict) -> dict:
        """Preview orders without actually submitting them and get commission information in the response

        :param account_id: Account ID
        :type account_id: str
        :param order_info: Order information
        :type order_info: dict
        :return: Order preview information
        :rtype: dict
        """
        endpoint = f"iserver/account/{account_id}/orders/whatif"
        response = requests.post(f"{self.url}{endpoint}", json=order_info, verify=self.ssl)
        return response.json()

    def get_market_data(self, conids: str, fields: str, since: int = None) -> dict:
        """Get market data for the given conids

        :param conids: List of conids separated by comma
        :type conids: str
        :param fields: List of fields separated by comma
        :type fields: str
        :param since: Time period since which updates are required (epoch time with milliseconds), optional
        :type since: int
        :return: Market data for the given conids
        :rtype: dict
        """
        params = {
            "conids": conids,
            "fields": fields
        }
        if since:
            params["since"] = since
        endpoint = "iserver/marketdata/snapshot"
        response = requests.get(f"{self.url}{endpoint}", params=params, verify=self.ssl)
        return response.json()

    def cancel_market_data(self, conid: str) -> dict:
        """Cancel market data for the given conid

        :param conid: Contract ID
        :type conid: str
        :return: Confirmation of market data cancellation
        :rtype: dict
        """
        endpoint = f"iserver/marketdata/{conid}/unsubscribe"
        response = requests.get(f"{self.url}{endpoint}", verify=self.ssl)
        return response.json()

    def get_performance(self) -> dict:
        """Returns the performance object

        :return: Performance object
        :rtype: dict
        """
        response = requests.get(f"{self.url}pa/performance", verify=self.ssl)
        return response.json()

    def get_transactions(self) -> dict:
        """Returns the transactions object

        :return: Transactions object
        :rtype: dict
        """
        response = requests.get(f"{self.url}pa/transactions", verify=self.ssl)
        return response.json()



    def reply_yes(self, id: str) -> dict:
        """
        Replies yes to a single message generated while submitting or modifying orders.

        :param id: message ID
        :type id: str
        :return: Returned message
        :rtype: dict
        """

        answer = {"confirmed": True}
        response = requests.post(
            f"{self.url}iserver/reply/{id}", json=answer, verify=self.ssl
        )

        return response.json()[0]

    def _reply_all_yes(self, response, reply_yes_to_all: bool) -> dict:
        """
        Replies yes to consecutive messages generated while submitting or modifying orders.
        """
        dic = response.json()[0]
        if reply_yes_to_all:
            while "order_id" not in dic.keys():
                print("Answering yes to ...")
                print(dic["message"])
                dic = self.reply_yes(dic["id"])
        return dic

    def submit_orders(self, list_of_orders: list, reply_yes=True) -> dict:
        """Submit a list of orders

        :param list_of_orders: List of order dictionaries. For each order dictionary, see `here <https://www.interactivebrokers.com/api/doc.html#tag/Order/paths/~1iserver~1account~1{accountId}~1orders/post>`_ for more details.
        :type list_of_orders: list
        :param reply_yes: Replies yes to returning messages or not, defaults to True
        :type reply_yes: bool, optional
        :return: Response to the order request
        :rtype: dict
        """
        response = requests.post(
            f"{self.url}iserver/account/{self.id}/orders",
            json={"orders": list_of_orders},
            verify=self.ssl,
        )

        assert response.status_code == 200, response.json()

        return self._reply_all_yes(response, reply_yes)

    def get_order(self, orderId: str) -> dict:
        """Returns details of the order

        :param orderId: Order ID of the submitted order
        :type orderId: str
        :return: Details of the order
        :rtype: dict
        """
        response = requests.get(
            f"{self.url}iserver/account/order/status/{orderId}", verify=self.ssl
        )

        return response.json()

    def get_live_orders(self, filters: list = None) -> dict:
        """Returns list of live orders

        :param filters: List of filters for the returning response. Available items -- "inactive" "pending_submit" "pre_submitted" "submitted" "filled" "pending_cancel" "cancelled" "warn_state" "sort_by_time", defaults to []
        :type filters: list, optional
        :return: list of live orders
        :rtype: dict
        """
        if filters is None:
            filters = []
        response = requests.get(
            f"{self.url}iserver/account/orders",
            params={"filters": filters},
            verify=self.ssl,
        )

        return response.json()

    def cancel_order(self, orderId: str) -> dict:
        """Cancel the submitted order

        :param orderId: Order ID for the input order
        :type orderId: str
        :return: Response from the server
        :rtype: dict
        """
        response = requests.delete(
            f"{self.url}iserver/account/{self.id}/order/{orderId}", verify=self.ssl
        )

        return response.json()

    def modify_order(
        self, orderId: str = None, order: dict = None, reply_yes=True
    ) -> dict:
        """Modify submitted order

        :param orderId: Order ID of the submitted order, defaults to None
        :type orderId: str
        :param order: Order dictionary, defaults to None
        :type order: dict
        :param reply_yes: Replies yes to the returning messages, defaults to True
        :type reply_yes: bool, optional
        :return: Response from the server
        :rtype: dict
        """
        assert (
            orderId != None and order != None
        ), "Input parameters (orderId or order) are missing"

        response = requests.post(
            f"{self.url}iserver/account/{self.id}/order/{orderId}",
            json=order,
            verify=self.ssl,
        )

        return self._reply_all_yes(response, reply_yes)

    def ping_server(self) -> dict:
        """Tickle server for maintaining connection

        :return: Response from the server
        :rtype: dict
        """
        response = requests.post(f"{self.url}tickle", verify=self.ssl)
        return response.json()

    def get_auth_status(self) -> dict:
        """Returns authentication status

        :return: Status dictionary
        :rtype: dict
        """
        response = requests.post(f"{self.url}iserver/auth/status", verify=self.ssl)
        return response.json()

    def re_authenticate(self) -> None:
        """Attempts to re-authenticate when authentication is lost"""
        requests.post(f"{self.url}iserver/reauthenticate", verify=self.ssl)
        print("Reauthenticating ...")

    def log_out(self) -> None:
        """Log out from the gateway session"""
        requests.post(f"{self.url}logout", verify=self.ssl)

    def get_bars(
        self,
        symbol: str,
        period="1w",
        bar="1d",
        outsideRth=False,
        conid: str or int = "default",
    ) -> dict:
        """Returns market history for the given instrument. conid should be provided for futures and options.

        :param symbol: Symbol of the stock instrument
        :type symbol: str
        :param period: Period for the history, available time period-- {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y, defaults to "1w"
        :type period: str, optional
        :param bar: Granularity of the history, possible value-- 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m, defaults to "1d"
        :type bar: str, optional
        :param outsideRth: For contracts that support it, will determine if historical data includes outside of regular trading hours., defaults to False
        :type outsideRth: bool, optional
        :param conid: conid should be provided separately for futures or options. If not provided, it is assumed to be a stock.
        :type conid: str or int, optional
        :return: Response from the server
        :rtype: dict
        """
        if conid == "default":
            conid = self.get_conid(symbol)

        query = {
            "conid": int(conid),
            "period": period,
            "bar": bar,
            "outsideRth": outsideRth,
        }
        response = requests.get(
            f"{self.url}iserver/marketdata/history", params=query, verify=self.ssl
        )

        return response.json()

    def get_fut_conids(self, symbol: str) -> list:
        """Returns list of contract id objects of a future instrument.

        :param symbol: symbol of a future instrument
        :type symbol: str
        :return: list of contract id objects
        :rtype: list
        """
        query = {"symbols": symbol}
        response = requests.get(
            f"{self.url}trsrv/futures", params=query, verify=self.ssl
        )

        return response.json()[symbol]



if __name__ == "__main__":

    api = REST()

    # print(api.reply_yes("a37bcc93-736b-441b-88a3-ee291d5dbcbd"))
    orders = [
        {
            "conid": api.get_conid("AAPL"),
            "orderType": "MKT",
            "side": "BUY",
            "quantity": 7,
            "tif": "GTC",
        }
    ]

    # print(api.submit_order(orders))
    # print(api.modify_order(1258176643, orders[0]))
    # print(api.get_order(1258176642))
    # print(api.get_portfolio())
    # print(api.re_authenticate())
    # print(api.get_auth_status())
    # print(api.get_live_orders())
    # print(api.get_bars("TSLA"))
    # print(api.get_conid("AAPL"))
    # print(api.get_conid("MUB", contract_filters={"isUS": True, "exchange": "ARCA"}))
    # print(api.get_conid("MUB", instrument_filters={"name": "ISHARES NATIONAL MUNI BOND E", "assetClass": "STK"}))
    # print(api.cancel_order(2027388848))
