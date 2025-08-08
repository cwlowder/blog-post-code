mod complex {
    include!(concat!(env!("OUT_DIR"), "/complex.rs"));
}
use crate::product::Product;

use rand::{distributions::Alphanumeric, Rng};

fn random_string(rng: &mut impl Rng, len: usize) -> String {
    rng.sample_iter(&Alphanumeric).take(len).map(char::from).collect()
}

pub fn generate_random_product() -> Product {
    let mut rng = rand::thread_rng();
    let len = rng.gen_range(5..10);
    Product {
        id: rng.gen(),
        price: rng.gen_range(1.0..1000.0),
        in_stock: rng.gen_bool(0.5),
        tags: vec!["benchmark".into(), "test".into()],
        name: random_string(&mut rng, len),
    }
}