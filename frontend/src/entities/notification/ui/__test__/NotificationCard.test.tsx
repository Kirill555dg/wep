import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NotificationCard } from "../NotificationCard";
import { Notification } from "../../model/types";

const mockNotification: Notification = {
  id: 1,
  type: "homework_new",
  title: "Новое задание",
  description: "Сдайте уравнения",
  date: "2025-05-11T14:30:00",
  read: false,
  link: "/homework/1",
  linkText: "Перейти",
  classTitle: "Математика 10А",
};

describe("NotificationCard", () => {
  it("рендерит заголовок, описание и кнопку перехода", () => {
    render(<NotificationCard notification={mockNotification} onNavigate={vi.fn()} />);

    expect(screen.getByRole("heading", { name: /новое задание/i })).toBeInTheDocument();
    expect(screen.getByText(/сдайте уравнения/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /перейти/i })).toBeInTheDocument();
  });

  it("отображает кнопку 'Прочитано', если уведомление не прочитано", () => {
    render(<NotificationCard notification={mockNotification} onMarkRead={vi.fn()} />);

    expect(screen.getByRole("button", { name: /прочитано/i })).toBeInTheDocument();
  });

  it("не отображает кнопку 'Прочитано', если уведомление уже прочитано", () => {
    render(<NotificationCard notification={{ ...mockNotification, read: true }} />);

    expect(screen.queryByRole("button", { name: /прочитано/i })).not.toBeInTheDocument();
  });

  it("вызывает onMarkRead при клике по 'Прочитано'", async () => {
    const onMarkRead = vi.fn();

    render(<NotificationCard notification={mockNotification} onMarkRead={onMarkRead} />);

    await userEvent.click(screen.getByRole("button", { name: /прочитано/i }));
    expect(onMarkRead).toHaveBeenCalledWith(mockNotification.id);
  });

  it("вызывает onNavigate и onMarkRead при клике на 'Перейти'", async () => {
    const onNavigate = vi.fn();
    const onMarkRead = vi.fn();

    render(<NotificationCard notification={mockNotification} onNavigate={onNavigate} onMarkRead={onMarkRead} />);

    await userEvent.click(screen.getByRole("button", { name: /перейти/i }));
    expect(onMarkRead).toHaveBeenCalledWith(mockNotification.id);
    expect(onNavigate).toHaveBeenCalledWith(mockNotification.link);
  });
});
