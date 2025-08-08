mod random;
mod product;

use std::time::Instant;
use prost::Message;
// use bson::{to_bson, from_bson, Bson};
use bincode;
use rkyv::{to_bytes, rancor::Error};
use crate::product::Product;
use crate::product::to_proto_product;
use crate::product::ProductProto;
use crate::random::generate_random_product;

// use flatbuffers::{FlatBufferBuilder, WIPOffset};

const SKIP_DESERIALIZE : bool = false;

pub trait FormatBenchmark<T> {
    fn encode(item: &T) -> Vec<u8>;
    fn decode(bytes: &[u8]) -> T;
}


fn json_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;
    for item in data {
        let encoded = serde_json::to_string(item).unwrap();
        total_size += encoded.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded: Product = serde_json::from_str(&encoded).unwrap();

        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }
    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn cbor_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;
    for item in data {
        let encoded = serde_cbor::to_vec(item).unwrap();
        total_size += encoded.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded: Product = serde_cbor::from_slice(&encoded).unwrap();
        
        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }
    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn ciborium_benchmark(data: &Vec<Product>) -> (f64, usize) {
    use ciborium::{de::from_reader, ser::into_writer};

    let start = Instant::now();
    let mut total_size = 0;

    for item in data {
        let mut buffer = Vec::new();

        // Encode
        into_writer(item, &mut buffer).expect("Failed to encode with ciborium");
        total_size += buffer.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        // Decode
        let decoded: Product = from_reader(buffer.as_slice()).expect("Failed to decode with ciborium");

        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }

    (start.elapsed().as_secs_f64(), total_size)
}

fn msgpack_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;
    for item in data {
        let encoded = rmp_serde::to_vec(item).unwrap();
        total_size += encoded.len();
        
        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded: Product = rmp_serde::from_slice(&encoded).unwrap();
        
        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }
    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn protobuf_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;
    for item in data {
        let proto = ProductProto {
            id: item.id,
            name: item.name.clone(),
            price: item.price,
            in_stock: item.in_stock,
            tags: item.tags.clone(),
        };
        let encoded = proto.encode_to_vec();
        total_size += encoded.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded = ProductProto::decode(&*encoded).unwrap();

        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }
    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn protobuf_fixed_benchmark(data: &Vec<ProductProto>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;
    for item in data {
        let encoded = item.encode_to_vec();
        total_size += encoded.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded = ProductProto::decode(&*encoded).unwrap();
        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }
    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn rkyv_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = std::time::Instant::now();
    let mut total_size = 0;

    for item in data {
        let bytes = to_bytes::<Error>(item).expect("Failed to serialize with rkyv");
        total_size += bytes.len();


        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded = rkyv::access::<product::ArchivedProduct, Error>(&bytes).expect("Failed to access archived data");

        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }

    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn rkyv_unchecked_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = std::time::Instant::now();
    let mut total_size = 0;

    for item in data {
        let bytes = to_bytes::<Error>(item).expect("Failed to serialize with rkyv");
        total_size += bytes.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        let decoded = unsafe {rkyv::access_unchecked::<product::ArchivedProduct>(&bytes)};

        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }

    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

fn bincode_benchmark(data: &Vec<Product>) -> (f64, usize) {
    let start = Instant::now();
    let mut total_size = 0;

    let config = bincode::config::standard();

    for item in data {
        // Encode
        let encoded = bincode::encode_to_vec(item, config).unwrap();
        total_size += encoded.len();

        if SKIP_DESERIALIZE {
            continue;
        }

        // Decode
        let decoded: Product = bincode::decode_from_slice(&encoded, config)
            .unwrap()
            .0;
        // Prevent dead code optimization
        assert_eq!(decoded.id, item.id);
    }

    let duration = start.elapsed().as_secs_f64();
    (duration, total_size)
}

// fn bson_benchmark(data: &Vec<Product>) -> (f64, usize) {
//     let start = std::time::Instant::now();
//     let mut total_size = 0;

//     for item in data {
//         // Serialize to bson::Bson
//         let bson_value = to_bson(item).expect("Failed to serialize to BSON");

//         // Convert bson::Bson to raw bytes (Vec<u8>)
//         let encoded = bson::to_vec(bson_value.as_document()
//             .expect("Expected BSON document")).expect("Expected Vec<u8>");

//         total_size += encoded.len();

//         // Deserialize back from bytes
//         let decoded_doc = bson::Document::from_reader(&mut encoded.as_slice())
//             .expect("Failed to deserialize BSON document");

//         let _decoded: Product = from_bson(Bson::Document(decoded_doc))
//             .expect("Failed to deserialize BSON into Product");
//     }

//     let duration = start.elapsed().as_secs_f64();
//     (duration, total_size)
// }


fn theoretical_minimum(data: &Vec<Product>) -> (f64, usize) {
    let mut total_size = 0;

    for item in data {
        // u64: 8 bytes
        let id_size = 8;

        // f64: 8 bytes
        let price_size = 8;

        // bool: 1 byte
        let in_stock_size = 1;

        // String: UTF-8 byte length
        let name_size = item.name.as_bytes().len();

        // Vec<String>: sum of lengths of all tag strings (UTF-8 byte length)
        let tags_size: usize = item.tags.iter().map(|tag| tag.len()).sum();

        total_size += id_size + price_size + in_stock_size + name_size + tags_size;
    }

    (-1.0, total_size)
}

fn print_stats(name: &str, n_iters: usize, time: f64, size: f64, theoretical_minimum_size: f64) {
    println!("{:<13} | {:>9.2} | {:>14.2} | {:>17.2} | {:>7.2}% |", name, time * 1000.0, time * 1_000_000_000.0 / (n_iters as f64), size / n_iters as f64, -100.0 + 100.0 * size as f64 / theoretical_minimum_size);
}


fn main() {
    const N: usize = 1_000_000;
    let data: Vec<Product> = (0..N).map(|_| generate_random_product()).collect();
    let data_proto: Vec<ProductProto> = data.iter().into_iter().map(|p| to_proto_product(&p)).collect();

    let (json_time, json_size) = json_benchmark(&data);
    // let (bson_time, bson_size) = bson_benchmark(&data);
    let (cbor_time, cbor_size) = cbor_benchmark(&data);
    let (ciborium_time, ciborium_size) = ciborium_benchmark(&data);
    let (msgpack_time, msgpack_size) = msgpack_benchmark(&data);
    let (protobuf_time, protobuf_size) = protobuf_benchmark(&data);
    let (protobuf_fixed_time, protobuf_fixed_size) = protobuf_fixed_benchmark(&data_proto);
    let (rkyv_time, rkyv_size) = rkyv_benchmark(&data);
    let (rkyv_unchecked_time, rkyv_unchecked_size) = rkyv_unchecked_benchmark(&data);
    let (bincode_time, bincode_size) = bincode_benchmark(&data);
    let (_, theoretical_minimum_size) = theoretical_minimum(&data);

    println!("Benchmark Results ({} entries):", N);
    println!("--------------|-----------|----------------|-------------------|----------|");
    println!("Format        | Time (ms) |  Avg Time (ns) |  Avg Size (bytes) | Overhead |");
    println!("--------------|-----------|----------------|-------------------|----------|");
    print_stats("JSON", N, json_time, json_size as f64, theoretical_minimum_size as f64);
    print_stats("CBOR", N, cbor_time, cbor_size as f64, theoretical_minimum_size as f64);
    print_stats(" ⮡ CIBORIUM", N, ciborium_time, ciborium_size as f64, theoretical_minimum_size as f64);
    print_stats("MessagePack", N, msgpack_time, msgpack_size as f64, theoretical_minimum_size as f64);
    print_stats("Protobuf", N, protobuf_time, protobuf_size as f64, theoretical_minimum_size as f64);
    print_stats(" ⮡ No Copies", N, protobuf_fixed_time, protobuf_fixed_size as f64, theoretical_minimum_size as f64);
    print_stats("Rkyv", N, rkyv_time, rkyv_size as f64, theoretical_minimum_size as f64);
    print_stats(" ⮡ unsafe", N, rkyv_unchecked_time, rkyv_unchecked_size as f64, theoretical_minimum_size as f64);
    print_stats("BINCODE", N, bincode_time, bincode_size as f64, theoretical_minimum_size as f64);
    println!("Theoretical   | {:>9} | {:>14} | {:>17.2} | {:>7.2}% |", "N/A", "N/A", theoretical_minimum_size as f64 / N as f64, -100.0 + 100.0 * theoretical_minimum_size as f64 / theoretical_minimum_size as f64);
    // println!("BSON          | {:>9.2} | {:>17.2} | {:>7.2}%", bson_time * 1000.0, bson_size as f64 / N as f64, -100.0 + 100.0 * bson_size as f64 / theoretical_minimum_size as f64);
}
