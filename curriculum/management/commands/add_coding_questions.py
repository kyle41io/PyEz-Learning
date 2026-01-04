from django.core.management.base import BaseCommand
from curriculum.models import Lesson

class Command(BaseCommand):
    help = 'Add coding questions to lessons'

    def handle(self, *args, **kwargs):
        lessons_data = {
            3: {
                "title": "Các lệnh vào ra đơn giản",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình Python yêu cầu người dùng nhập tên của họ và in ra lời chào.\n\nYêu cầu:\n- Sử dụng hàm input() để nhận tên từ người dùng\n- In ra câu: 'Xin chào, [tên]!' (trong đó [tên] là tên người dùng nhập vào)\n\nVí dụ:\nNếu người dùng nhập: 'An'\nChương trình sẽ in ra: 'Xin chào, An!'",
                        "test_cases": [
                            {"input": "An", "expected_output": "Xin chào, An!"},
                            {"input": "Minh", "expected_output": "Xin chào, Minh!"},
                            {"input": "Linh Nguyen", "expected_output": "Xin chào, Linh Nguyen!"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n# Sử dụng input() để nhận tên từ người dùng\n# In ra lời chào\n\n"
                    }
                ]
            },
            4: {
                "title": "Câu lệnh rẽ nhánh If",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình nhận một số nguyên từ người dùng và kiểm tra xem số đó là số chẵn hay số lẻ.\n\nYêu cầu:\n- Sử dụng input() để nhận số từ người dùng\n- Chuyển đổi thành số nguyên bằng int()\n- Nếu số chẵn, in ra: 'Số chẵn'\n- Nếu số lẻ, in ra: 'Số lẻ'\n\nGợi ý: Sử dụng toán tử % để kiểm tra số dư khi chia cho 2",
                        "test_cases": [
                            {"input": "4", "expected_output": "Số chẵn"},
                            {"input": "7", "expected_output": "Số lẻ"},
                            {"input": "0", "expected_output": "Số chẵn"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nn = int(input())\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình nhận một số từ người dùng và xác định số đó là dương, âm hay bằng 0.\n\nYêu cầu:\n- Nhận một số từ người dùng\n- Nếu số > 0, in ra: 'Số dương'\n- Nếu số < 0, in ra: 'Số âm'\n- Nếu số = 0, in ra: 'Bằng không'",
                        "test_cases": [
                            {"input": "5", "expected_output": "Số dương"},
                            {"input": "-3", "expected_output": "Số âm"},
                            {"input": "0", "expected_output": "Bằng không"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nn = int(input())\n\n"
                    }
                ]
            },
            5: {
                "title": "Câu lệnh lặp For",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình in ra các số từ 1 đến 5, mỗi số trên một dòng.\n\nYêu cầu:\n- Sử dụng vòng lặp for\n- In ra các số: 1, 2, 3, 4, 5 (mỗi số trên một dòng)",
                        "test_cases": [
                            {"input": "", "expected_output": "1\n2\n3\n4\n5"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n# Sử dụng vòng lặp for với range()\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình tính tổng các số từ 1 đến 10.\n\nYêu cầu:\n- Sử dụng vòng lặp for\n- Tính tổng 1 + 2 + 3 + ... + 10\n- In ra kết quả (số 55)",
                        "test_cases": [
                            {"input": "", "expected_output": "55"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ntong = 0\n# Sử dụng vòng lặp for để cộng các số\n\n"
                    }
                ]
            },
            6: {
                "title": "Câu lệnh While",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình đếm ngược từ 5 về 1, mỗi số trên một dòng.\n\nYêu cầu:\n- Sử dụng vòng lặp while\n- In ra các số: 5, 4, 3, 2, 1 (mỗi số trên một dòng)",
                        "test_cases": [
                            {"input": "", "expected_output": "5\n4\n3\n2\n1"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nn = 5\n# Sử dụng vòng lặp while\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình nhận các số từ người dùng cho đến khi người dùng nhập số 0, sau đó in ra tổng các số đã nhập (không tính số 0).\n\nYêu cầu:\n- Sử dụng vòng lặp while\n- Khi người dùng nhập 0, dừng lại và in tổng",
                        "test_cases": [
                            {"input": "5\n3\n2\n0", "expected_output": "10"},
                            {"input": "1\n1\n1\n1\n0", "expected_output": "4"},
                            {"input": "0", "expected_output": "0"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ntong = 0\n# Sử dụng vòng lặp while\n\n"
                    }
                ]
            },
            8: {
                "title": "Một số lệnh làm việc với list",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình tạo một danh sách gồm 5 số: [10, 20, 30, 40, 50] và in ra phần tử đầu tiên và phần tử cuối cùng.\n\nYêu cầu:\n- Tạo list: [10, 20, 30, 40, 50]\n- In ra phần tử đầu tiên (10)\n- In ra phần tử cuối cùng (50)",
                        "test_cases": [
                            {"input": "", "expected_output": "10\n50"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nds = [10, 20, 30, 40, 50]\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình tạo một danh sách rỗng, thêm 3 số (1, 2, 3) vào danh sách bằng phương thức append(), sau đó in ra độ dài của danh sách.\n\nYêu cầu:\n- Tạo list rỗng\n- Thêm các số 1, 2, 3 bằng append()\n- In ra độ dài (số 3)",
                        "test_cases": [
                            {"input": "", "expected_output": "3"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nds = []\n\n"
                    }
                ]
            },
            10: {
                "title": "Một số lệnh làm việc với chuỗi",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình nhận một chuỗi từ người dùng và in ra chuỗi đó dưới dạng chữ HOA.\n\nYêu cầu:\n- Nhận chuỗi từ người dùng\n- Chuyển đổi thành chữ HOA bằng phương thức upper()\n- In ra kết quả",
                        "test_cases": [
                            {"input": "hello", "expected_output": "HELLO"},
                            {"input": "Python", "expected_output": "PYTHON"},
                            {"input": "xin chào", "expected_output": "XIN CHÀO"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ns = input()\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình nhận một chuỗi từ người dùng và đếm số ký tự trong chuỗi đó (không tính khoảng trắng).\n\nYêu cầu:\n- Nhận chuỗi từ người dùng\n- Đếm số ký tự không bao gồm khoảng trắng\n- In ra số lượng",
                        "test_cases": [
                            {"input": "hello", "expected_output": "5"},
                            {"input": "xin chao", "expected_output": "7"},
                            {"input": "a b c", "expected_output": "3"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ns = input()\n\n"
                    }
                ]
            },
            11: {
                "title": "Hàm trong Python",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết một hàm tên là chao() không có tham số, khi được gọi sẽ in ra 'Xin chào!'. Sau đó gọi hàm này.\n\nYêu cầu:\n- Định nghĩa hàm chao()\n- Hàm in ra 'Xin chào!'\n- Gọi hàm",
                        "test_cases": [
                            {"input": "", "expected_output": "Xin chào!"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n# Định nghĩa hàm chao()\n\n# Gọi hàm\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết một hàm tên là binh_phuong() nhận một số làm tham số và trả về bình phương của số đó. Sau đó gọi hàm với số 5 và in ra kết quả.\n\nYêu cầu:\n- Định nghĩa hàm binh_phuong(n)\n- Hàm trả về n * n\n- Gọi hàm với số 5 và in kết quả (25)",
                        "test_cases": [
                            {"input": "", "expected_output": "25"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n# Định nghĩa hàm binh_phuong(n)\n\n# Gọi hàm và in kết quả\n"
                    }
                ]
            },
            12: {
                "title": "Tham số hàm",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết một hàm tong(a, b) nhận hai số và trả về tổng của chúng. Gọi hàm với 3 và 7, in ra kết quả.\n\nYêu cầu:\n- Định nghĩa hàm tong(a, b)\n- Trả về a + b\n- Gọi hàm với 3 và 7, in kết quả (10)",
                        "test_cases": [
                            {"input": "", "expected_output": "10"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết một hàm chao_ten(ten='Bạn') có tham số mặc định. Hàm in ra 'Xin chào, [ten]!'. Gọi hàm hai lần: một lần không có tham số và một lần với tham số 'An'.\n\nYêu cầu:\n- Định nghĩa hàm với tham số mặc định\n- Gọi hai lần và in kết quả",
                        "test_cases": [
                            {"input": "", "expected_output": "Xin chào, Bạn!\nXin chào, An!"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    }
                ]
            },
            13: {
                "title": "Phạm vi biến",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình tạo một biến toàn cục x = 10, sau đó tạo một hàm in_x() để in giá trị của x. Gọi hàm này.\n\nYêu cầu:\n- Tạo biến x = 10 bên ngoài hàm\n- Định nghĩa hàm in_x() in ra x\n- Gọi hàm (kết quả: 10)",
                        "test_cases": [
                            {"input": "", "expected_output": "10"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết một hàm doi_gia_tri() sử dụng từ khóa global để thay đổi giá trị của biến toàn cục y từ 5 thành 15. In ra y trước và sau khi gọi hàm.\n\nYêu cầu:\n- Tạo y = 5\n- In y (5)\n- Định nghĩa hàm thay đổi y thành 15\n- Gọi hàm\n- In y (15)",
                        "test_cases": [
                            {"input": "", "expected_output": "5\n15"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ny = 5\n\n"
                    }
                ]
            },
            14: {
                "title": "Nhận biết lỗi chương trình",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình sử dụng try-except để xử lý lỗi khi chia một số cho 0. Nhận hai số từ người dùng, thực hiện phép chia. Nếu chia cho 0, in 'Lỗi: Không thể chia cho 0', ngược lại in kết quả.\n\nYêu cầu:\n- Nhận hai số a và b\n- Thử chia a cho b\n- Xử lý ngoại lệ ZeroDivisionError",
                        "test_cases": [
                            {"input": "10\n2", "expected_output": "5.0"},
                            {"input": "10\n0", "expected_output": "Lỗi: Không thể chia cho 0"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\na = int(input())\nb = int(input())\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình nhận một chuỗi từ người dùng và thử chuyển đổi thành số nguyên. Nếu thành công, in ra số đó. Nếu thất bại, in 'Lỗi: Không phải số'.\n\nYêu cầu:\n- Nhận chuỗi từ người dùng\n- Thử chuyển đổi thành int\n- Xử lý ngoại lệ ValueError",
                        "test_cases": [
                            {"input": "123", "expected_output": "123"},
                            {"input": "abc", "expected_output": "Lỗi: Không phải số"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ns = input()\n\n"
                    }
                ]
            },
            15: {
                "title": "Kiểm thử và gỡ lỗi chương trình",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết hàm kiem_tra_so_duong(n) kiểm tra xem một số có phải là số dương không. Trả về True nếu đúng, False nếu sai. Test với số 5 và -3.\n\nYêu cầu:\n- Định nghĩa hàm kiem_tra_so_duong(n)\n- Trả về True nếu n > 0, ngược lại False\n- Test và in kết quả cho cả hai trường hợp",
                        "test_cases": [
                            {"input": "", "expected_output": "True\nFalse"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết hàm tim_max(a, b, c) trả về số lớn nhất trong ba số. Test với 5, 12, 8.\n\nYêu cầu:\n- Định nghĩa hàm tim_max(a, b, c)\n- Trả về số lớn nhất\n- Gọi với 5, 12, 8 và in kết quả (12)",
                        "test_cases": [
                            {"input": "", "expected_output": "12"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    }
                ]
            },
            16: {
                "title": "Thực hành viết các chương trình đơn giản",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết chương trình nhận một số nguyên n từ người dùng và in ra bảng cửu chương của n từ 1 đến 10.\n\nYêu cầu:\n- Nhận số n\n- In ra: n x 1 = kết quả, n x 2 = kết quả, ..., n x 10 = kết quả\n- Mỗi dòng một phép tính\n\nVí dụ với n=2:\n2 x 1 = 2\n2 x 2 = 4\n...\n2 x 10 = 20",
                        "test_cases": [
                            {"input": "3", "expected_output": "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15\n3 x 6 = 18\n3 x 7 = 21\n3 x 8 = 24\n3 x 9 = 27\n3 x 10 = 30"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nn = int(input())\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình tính giai thừa của một số n (n!).\n\nYêu cầu:\n- Nhận số n từ người dùng\n- Tính n! = n × (n-1) × (n-2) × ... × 1\n- In ra kết quả\n\nVí dụ: 5! = 5 × 4 × 3 × 2 × 1 = 120",
                        "test_cases": [
                            {"input": "5", "expected_output": "120"},
                            {"input": "3", "expected_output": "6"},
                            {"input": "1", "expected_output": "1"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\nn = int(input())\n\n"
                    }
                ]
            },
            17: {
                "title": "Ôn tập lập trình Python",
                "questions": [
                    {
                        "question_id": 1,
                        "question": "Viết hàm kiem_tra_nguyen_to(n) kiểm tra xem một số có phải là số nguyên tố không. Trả về True nếu đúng, False nếu sai. Test với số 7 và 8.\n\nYêu cầu:\n- Số nguyên tố là số chỉ chia hết cho 1 và chính nó\n- Test và in kết quả",
                        "test_cases": [
                            {"input": "", "expected_output": "True\nFalse"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    },
                    {
                        "question_id": 2,
                        "question": "Viết chương trình đảo ngược một chuỗi. Nhận chuỗi từ người dùng và in ra chuỗi đảo ngược.\n\nYêu cầu:\n- Nhận chuỗi từ người dùng\n- Đảo ngược chuỗi\n- In ra kết quả\n\nVí dụ: 'hello' -> 'olleh'",
                        "test_cases": [
                            {"input": "hello", "expected_output": "olleh"},
                            {"input": "Python", "expected_output": "nohtyP"},
                            {"input": "123", "expected_output": "321"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\ns = input()\n\n"
                    },
                    {
                        "question_id": 3,
                        "question": "Viết chương trình tạo một dictionary (từ điển) chứa thông tin về một học sinh: tên, tuổi, lớp. Sau đó in ra từng thông tin.\n\nYêu cầu:\n- Tạo dict: {'ten': 'An', 'tuoi': 15, 'lop': '10A'}\n- In ra: An, 15, 10A (mỗi giá trị trên một dòng)",
                        "test_cases": [
                            {"input": "", "expected_output": "An\n15\n10A"}
                        ],
                        "starter_code": "# Viết code của bạn ở đây\n\n"
                    }
                ]
            }
        }
        
        # Process each lesson
        for lesson_order, data in lessons_data.items():
            try:
                lesson = Lesson.objects.get(order=lesson_order)
                lesson.coding = data["questions"]
                lesson.save()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Lesson {lesson_order}: {data["title"]} - Added {len(data["questions"])} question(s)'
                ))
            except Lesson.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'✗ Lesson {lesson_order} not found - skipped'
                ))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Coding questions import completed!'))
