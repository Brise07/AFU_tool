from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib import colors
from tkinter import filedialog, messagebox
import os
import tempfile
from PIL import ImageGrab

# Color mapping dictionary
COLOR_MAP = {
    "lightgray": "#D3D3D3",
    "lightblue": "#ADD8E6",
    "yellow": "#FFFF00",
    "red": "#FF0000",
    "green": "#00FF00",
    "black": "#000000"
}

def get_image(root, widget):
    # Get absolute screen coordinates of the widget
    x = widget.winfo_rootx() #+ widget.winfo_x()
    y = widget.winfo_rooty() #+ widget.winfo_y()
    x1 = x + widget.winfo_width()+200
    y1 = y + widget.winfo_height()+200
    return ImageGrab.grab().crop((x, y, x1, y1))

def export_to_pdf(application):
    """Exports the fire regulation results to a PDF file, automatically adding pages if needed."""

    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    try:
        tk_canvas = application.app_frame.room_canvas  # Access canvas correctly

        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
            temp_img_path = temp_img.name
            canvas_image = get_image(application, tk_canvas)  # Get canvas image
            canvas_image.save(temp_img_path, format='PNG')

        # Create PDF
        pdf = rl_canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Fire Regulation and Universal Design Compliance Results")
        pdf.drawImage(temp_img_path, 50, height - 400, width=canvas_image.width/2.5, height=canvas_image.height/2.5, preserveAspectRatio=True)

        y_position = height - 450
        black_text = COLOR_MAP.get("black")
        rooms = [room_item.room for room_item in application.app_frame.room_canvas.rooms.values() if room_item.room.is_part_of_escape_route]

        for i, error_msg in enumerate(application.result.get_result_messages()):
            calculated, text_color, room_color, result = error_msg
            room = rooms[i]
            text_color = COLOR_MAP.get(text_color.lower(), "#000000")
            room_color = COLOR_MAP.get(room_color.lower(), "#FFFFFF")

            if y_position < 100:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y_position = height - 50

            pdf.setFont("Helvetica", 12)
            pdf.setFillColor(colors.HexColor(black_text))
            pdf.drawString(50, y_position, f"Room: {room.name} - {room.long_name}")
            y_position -= 30

            # Draw the room color
            pdf.setFillColor(colors.HexColor(room_color))
            pdf.rect(50, y_position, 20, 20, fill=1)

            pdf.setFont("Helvetica", 10)
            pdf.setFillColor(colors.HexColor(black_text))
            pdf.drawString(100, y_position, calculated)

            pdf.setFillColor(colors.HexColor(text_color))
            for text in result.split('\n'):
                if y_position < 100:  # New page needed during text wrap
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y_position = height - 50

                y_position -= 15
                pdf.drawString(50, y_position, text)
            y_position -= 30

        pdf.save()
        messagebox.showinfo("Export", "PDF has been generated successfully.")

    except Exception as e:
        print(str(e))
        messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")
    finally:
        # Clean up temporary files
        if 'temp_img_path' in locals():
            try:
                os.unlink(temp_img_path)
            except Exception as cleanup_err:
                print(f"Error cleaning up temporary file: {cleanup_err}")
                pass