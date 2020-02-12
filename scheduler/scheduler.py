from collections import OrderedDict


class Colors:
    red = 'red'
    blue = 'blue'
    green = 'green'
ORDERATE = 'orderdate'
ADDR = 'addr'
STATSU = 'stats'
class DeliveryStatus:
    pending = 'pending'
    complete = 'complete'
MAX_CAPA = 20


current_lap = OrderedDict()


class DataBase:
    def __init__(self):
        self.pending_orders = OrderedDict()
        self.cursor = None
        self.db = None

    def fetch_pending_orders(self):
        query = 'SELECT * FROM orders WHERE pending = 1'
        self.cursor.exucute(query)
        return [Order.from_db(order) for order in self.cursor.fetchall()]

    def update_pending_orders(self):
        all_pending_orders = self.fetch_pending_orders()
        for po in all_pending_orders:
            if po.id_ not in self.pending_orders:
                self.pending_orders[po.id_] = po
        return self.pending_orders

    def mark_complete(self, id_):
        self.pending.pop(id_)
        # TODO: mysql query to UPDATE filldate


class Order:
    def __init__(self, id_, addr, r, g, b, orderdate, pending=True):
        self.id_ = id_
        self.addr, self.r, self.g, self.b = addr, r, g, b
        self.orderdate = orderdate
        self.pending = pending

    def partial_complete(self, completed):
        self.r -= completed[Colors.red]
        self.g -= completed[Colors.green]
        self.b -= completed[Colors.blue]
        self.may_mark_complete()

    def may_mark_complete(self):
        if all([item == 0 for item in [self.red, self.green, self.blue]]):
            self.pending = False

    @classmethod
    def from_db(cls, order):
        id_, name, r, g, b, pending, orderdate, filldate, addr = order
        return cls(id_, addr, r, g, b, orderdate)


class Delivery:
    def __init__(self, parent_order, addr, r, g, b):
        self.parent_order = parent_order
        self.addr, self.r, self.g, self.b = addr, r, g, b
        self.status = DeliveryStatus.pending

    def complete(self):
        self.parent_order.partial_complete(self.to_dict())

    def to_dict(self):
        return {Colors.red: self.r, Colors.green: self.g, Colors.blue: self.b,
                STATUS: self.status}

    @property
    def num_items(self):
        return self.r + self.g + self.b

class Lap:
    def __init__(self, deliv_list):
        addr_set = set([deliv.addr for deliv in deliv_list])
        assert len(addr_set) == len(deliv_list)
        self.deliveries = {deliv.addr: deliv for deliv in deliv_list}

    def get_delivery(self, addr):
        return self.deliveries[addr]


class BaseScheduler:
    def __init__(self, database, max_capa=MAX_CAPA):
        self.database = database
        self.max_capa = max_capa

class FCFSScheduler(BaseScheduler):
    def __init__(self, database):
        super().__init__(database)

    def make_deliv_list(self, pending_orders):
        pending_orders = self.database.update_pending_orders()

        loaded = 0
        while loaded <= self.max_capa:
            pass

        return Lap()


