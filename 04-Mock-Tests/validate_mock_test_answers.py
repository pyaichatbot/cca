from __future__ import annotations

import argparse
from collections import defaultdict
import re
import sys
from pathlib import Path


ROW_PATTERN = re.compile(r"^\|\s*(\d+)\s*\|\s*([A-Da-d]?)\s*\|")
KEY_PATTERN = re.compile(r"^\|\s*(\d+)\s*\|\s*([A-D])\s*\|")
KEY_WITH_DOMAIN_PATTERN = re.compile(r"^\|\s*(\d+)\s*\|\s*([A-D])\s*\|\s*([^|]+?)\s*\|")


def parse_answer_file(path: Path) -> dict[int, str]:
    answers: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW_PATTERN.match(line)
        if not match:
            continue
        question = int(match.group(1))
        answer = match.group(2).upper()
        answers[question] = answer
    return answers


def parse_key_file(path: Path) -> dict[int, str]:
    key: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = KEY_PATTERN.match(line)
        if not match:
            continue
        question = int(match.group(1))
        answer = match.group(2)
        key[question] = answer
    return key


def parse_key_domains(path: Path) -> dict[int, str]:
    domains: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = KEY_WITH_DOMAIN_PATTERN.match(line)
        if not match:
            continue
        question = int(match.group(1))
        domain = match.group(3).strip()
        domains[question] = domain
    return domains


def format_validation_title(key_file: Path) -> str:
    return f"{key_file.stem.replace('-', ' ')} Validation"


def print_domain_breakdown(
    key: dict[int, str],
    domains: dict[int, str],
    correct: list[int],
    incorrect: list[tuple[int, str, str]],
    unanswered: list[int],
) -> None:
    if not domains:
        return

    totals: dict[str, int] = defaultdict(int)
    correct_counts: dict[str, int] = defaultdict(int)
    incorrect_counts: dict[str, int] = defaultdict(int)
    unanswered_counts: dict[str, int] = defaultdict(int)

    for question in key:
        domain = domains.get(question, "Unspecified")
        totals[domain] += 1

    for question in correct:
        domain = domains.get(question, "Unspecified")
        correct_counts[domain] += 1

    for question, _, _ in incorrect:
        domain = domains.get(question, "Unspecified")
        incorrect_counts[domain] += 1

    for question in unanswered:
        domain = domains.get(question, "Unspecified")
        unanswered_counts[domain] += 1

    print("\nDomain Breakdown:")
    for domain in sorted(totals):
        total = totals[domain]
        correct_total = correct_counts[domain]
        incorrect_total = incorrect_counts[domain]
        unanswered_total = unanswered_counts[domain]
        score = correct_total / total * 100 if total else 0.0
        print(
            f"  {domain}: {correct_total}/{total} ({score:.1f}%) | "
            f"incorrect {incorrect_total} | unanswered {unanswered_total}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a mock test answer sheet against the official answer key."
    )
    parser.add_argument("answer_file", type=Path, help="Path to the user answer markdown file")
    parser.add_argument(
        "--key-file",
        type=Path,
        default=Path(__file__).with_name("Mock-Test-1-Answers.md"),
        help="Path to the official answer key markdown file",
    )
    parser.add_argument(
        "--show-domains",
        action="store_true",
        help="Show domain-by-domain scoring when the answer key contains a Domain column.",
    )
    args = parser.parse_args()

    if not args.answer_file.exists():
        print(f"Answer file not found: {args.answer_file}", file=sys.stderr)
        return 1

    if not args.key_file.exists():
        print(f"Answer key file not found: {args.key_file}", file=sys.stderr)
        return 1

    answers = parse_answer_file(args.answer_file)
    key = parse_key_file(args.key_file)
    domains = parse_key_domains(args.key_file)

    if not key:
        print("No answer key entries were found.", file=sys.stderr)
        return 1

    correct = []
    incorrect = []
    unanswered = []

    for question in sorted(key):
        user_answer = answers.get(question, "")
        correct_answer = key[question]
        if not user_answer:
            unanswered.append(question)
        elif user_answer == correct_answer:
            correct.append(question)
        else:
            incorrect.append((question, user_answer, correct_answer))

    total_questions = len(key)
    answered_count = len(correct) + len(incorrect)
    score = len(correct) / total_questions * 100

    title = format_validation_title(args.key_file)
    print(title)
    print("=" * len(title))
    print(f"Answered:   {answered_count}/{total_questions}")
    print(f"Correct:    {len(correct)}")
    print(f"Incorrect:  {len(incorrect)}")
    print(f"Unanswered: {len(unanswered)}")
    print(f"Score:      {len(correct)}/{total_questions} ({score:.1f}%)")

    if args.show_domains:
        print_domain_breakdown(key, domains, correct, incorrect, unanswered)

    if incorrect:
        print("\nIncorrect answers:")
        for question, user_answer, correct_answer in incorrect:
            print(f"  Q{question}: your answer {user_answer}, correct answer {correct_answer}")

    if unanswered:
        unanswered_list = ", ".join(f"Q{question}" for question in unanswered)
        print(f"\nUnanswered: {unanswered_list}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())