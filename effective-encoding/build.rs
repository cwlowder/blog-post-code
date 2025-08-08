fn main() {
    prost_build::compile_protos(&["src/product.proto"], &["src/"])
        .expect("Failed to compile proto files");
}