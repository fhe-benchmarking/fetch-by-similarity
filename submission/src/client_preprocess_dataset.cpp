// client_preprocess_dataset.cpp - pre-processing the dataset before encryption
//============================================================================
// Copyright (c) 2025, Amazon Web Services
// All rights reserved.
//
// This software is licensed under the terms of the Apache License v2.
// See the file LICENSE.md for details.
//============================================================================
//FIXME: This is logically the right place to transpose the dataset matrix,
//  but for large datasets this will require a non-negligible additional
//  disk space to store both the original dataset and the transposed one.
//  Hence at least for now it is all done in client_encode_encrypt_db.
int main() { return 0; }
