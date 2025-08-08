use rkyv::{Archive, Serialize as RkyvSerialize, Deserialize as RkyvDeserialize};
mod benchmark {
    include!(concat!(env!("OUT_DIR"), "/benchmark.rs"));
}
pub use benchmark::Product as ProductProto;

#[derive(serde::Serialize, serde::Deserialize, Archive, RkyvSerialize, RkyvDeserialize, bincode::Decode, bincode::Encode, Debug, Clone)]
#[rkyv(
    compare(PartialEq),
    derive(Debug)
)]
pub(crate) struct Product {
    pub id: u64,
    pub name: String,
    pub price: f64,
    pub in_stock: bool,
    pub tags: Vec<String>,
}

pub fn to_proto_product(product: &Product) -> benchmark::Product {
    ProductProto {
        id: product.id,
        name: product.name.clone(),
        price: product.price,
        in_stock: product.in_stock,
        tags: product.tags.clone(),
    }
}