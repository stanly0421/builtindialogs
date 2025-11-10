#include "byterconverter.h"
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>

ByterConverter::ByterConverter(QWidget *parent)
    : QDialog(parent)
{
    QVBoxLayout* mainLayout= new QVBoxLayout (this);
    QGridLayout* editLayout = new QGridLayout;
    QHBoxLayout* buttonLayout = new QHBoxLayout;
    mainLayout->addLayout(editLayout);
    mainLayout->addStretch();
    mainLayout->addLayout (buttonLayout);
    QLabel* decLabel = new QLabel("十進位");
    QLabel* hexLabel = new QLabel("十六進位");
    QLabel* binLabel = new QLabel("二進位");
    decEdit = new QLineEdit;
    hexEdit = new QLineEdit;
    binEdit = new QLineEdit;
    editLayout->addWidget(decLabel,0,0);
    editLayout->addWidget(decEdit,0,1);
    editLayout->addWidget(hexLabel,1,0);
    editLayout->addWidget(hexEdit,1,1);
    editLayout->addWidget(binLabel,2,0);
    editLayout->addWidget(binEdit,2,1);
    QPushButton* exitButton = new QPushButton("Exit");
    buttonLayout->addStretch();
    buttonLayout->addWidget (exitButton);
    connect(exitButton,SIGNAL(clicked()),this,SLOT(accept()));
    connect(decEdit,SIGNAL(textChanged(const QString&)),
            this,SLOT(decChanged(const QString&)));
    connect(hexEdit,SIGNAL(textChanged(const QString&)),
            this,SLOT(hexChanged(const QString&)));
    connect(binEdit,SIGNAL(textChanged(const Qstring&)),
            this,SLOT(binChanged(const QString&)));
}
void ByterConverter:: decChanged(const QString& newValue)
{
        bool ok;
        int num=newValue.toInt(&ok);
        if (ok)
        {
            hexEdit->setText(QString::number(num, 16));
            binEdit->setText(QString::number(num,2));
        } else
        {
            hexEdit->setText("");
            binEdit->setText("");
        }
}
void ByterConverter:: hexChanged (const QString& newValue)
{   bool ok;
    int num = newValue.toInt (&ok, 16);
    if (ok)
    {
        decEdit->setText (QString::number (num, 10));
        binEdit->setText (QString::number(num,2));
    } else
    {
        decEdit->setText("");
        binEdit->setText("");
    }
}
void ByterConverter:: binChanged(const QString& newValue)
{
    bool ok;
    int num=newValue.toInt (&ok, 2);
    if (ok)
    {
        hexEdit->setText (QString::number(num, 16));
        decEdit->setText(QString::number (num, 10));
    } else
    {
        hexEdit->setText("");
        decEdit->setText("");
    }
}
ByterConverter::~ByterConverter() {}

