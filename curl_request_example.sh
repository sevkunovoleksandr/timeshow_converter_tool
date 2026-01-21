curl -X POST http://localhost:8081/convert_zip \
	-H "Content-Type: application/json" \
	-H "tsc-AccessKey: API" \
	-H "tsc-UserID: 1" \
	--data @Inputs/120.json \
	--output out.zip