pub struct Order {
    pub id: u64,
    pub amount: f64,
}

pub enum OrderStatus {
    Pending,
    Completed,
    Cancelled,
}

pub trait Processable {
    fn process(&self);
}

impl Processable for Order {
    fn process(&self) {
        println!("Processing order {}", self.id);
    }
}

pub fn create_order(id: u64, amount: f64) -> Order {
    Order { id, amount }
}
