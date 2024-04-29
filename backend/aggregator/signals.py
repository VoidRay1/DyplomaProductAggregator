from django import dispatch

product_parser_end_work_signal = dispatch.Signal(['updated_products'])