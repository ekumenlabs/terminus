/*
  The library cpuld be found on: https://code.google.com/archive/p/simple-svg/downloads
  To compile:
    mkdir build
    cd build
    cmake ..
    make
    ./sample-svg
*/
#include <simple_svg_1.0.0.hpp>

int main() {
  svg::Layout layout(svg::Dimensions(225, 225), svg::Layout::TopLeft, 1, svg::Point(0, 0));
  svg::Document doc("sample.svg", layout);

  doc.operator << (svg::Rectangle(svg::Point(25, 25), 200, 200,
                                  svg::Fill(svg::Color::Lime),
                                  svg::Stroke(1, svg::Color::Fuchsia)));

  doc.operator << (svg::Circle(svg::Point(135, 125), 75, svg::Fill(svg::Color::Orange)));

  svg::Polyline poly(svg::Fill(svg::Color::Transparent), svg::Stroke(4, svg::Color::Red));
  poly << svg::Point(50, 150);
  poly << svg::Point(50, 200);
  poly << svg::Point(200, 200);
  poly << svg::Point(200, 100);
  doc.operator << (poly);

  doc.operator << (svg::Line(svg::Point(50, 50),
                        svg::Point(200, 200),
                        svg::Stroke(4, svg::Color(0, 0, 255))));

  doc.save();

  return 0;
}